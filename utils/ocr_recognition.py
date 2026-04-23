"""
OCR文字识别工具模块
提供基于PaddleOCR的文本定位功能
支持MuMu模拟器通过ADB截图
"""

import cv2
import numpy as np
import subprocess
from PIL import Image
from io import BytesIO
from typing import Optional, Tuple, List, Dict
import logging

from utils.devices import ADB_PATH

# PaddleOCR 3.x
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    PaddleOCR = None

logger = logging.getLogger(__name__)

if not PADDLEOCR_AVAILABLE:
    logger.warning("⚠️ PaddleOCR未安装，OCR功能将不可用。请运行: pip install paddleocr>=3.0.0")


class OCRRecognition:
    """OCR文字识别工具类"""

    def __init__(self, device_port: int = 7555):
        """
        初始化OCR识别工具

        Args:
            device_port: MuMu模拟器ADB端口，默认7555
        """
        self.device_port = device_port
        self.device_serial = f"127.0.0.1:{device_port}"
        self.ocr_engine = None

        # 初始化PaddleOCR引擎（自动兼容 2.x / 3.x）
        if PADDLEOCR_AVAILABLE and PaddleOCR is not None:
            self.ocr_engine = PaddleOCR(
                use_textline_orientation=True,
                text_detection_model_name='PP-OCRv5_mobile_det',
                text_recognition_model_name='PP-OCRv5_mobile_rec',
                enable_mkldnn=False,
            )
            self._use_predict = hasattr(self.ocr_engine, 'predict')
        else:
            self._use_predict = False
            logger.warning("⚠️ PaddleOCR未安装，OCR功能不可用")

    def _run_adb_command(self, *args) -> Optional[bytes]:
        """
        执行ADB命令并返回原始输出

        Args:
            *args: ADB命令参数

        Returns:
            bytes: 命令输出，失败返回None
        """
        try:
            cmd = [ADB_PATH, "-s", self.device_serial] + list(args)
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"ADB命令执行失败: {result.stderr.decode()}")
                return None
        except subprocess.TimeoutExpired:
            logger.error("ADB命令执行超时")
            return None
        except Exception as e:
            logger.error(f"ADB命令异常: {e}")
            return None

    def take_screenshot(self) -> np.ndarray:
        """
        通过ADB截取当前屏幕

        Returns:
            numpy.ndarray: 屏幕截图的numpy数组 (RGB格式)
        """
        try:
            # 使用ADB截图命令直接获取PNG数据
            screenshot_data = self._run_adb_command("exec-out", "screencap", "-p")
            if screenshot_data is None:
                raise Exception("ADB截图失败")

            # 将PNG字节数据转换为图像
            image = Image.open(BytesIO(screenshot_data))
            return np.array(image)
        except Exception as e:
            logger.error(f"截屏失败: {e}")
            raise

    def find_element_by_ocr(self, text: str, region: Optional[Tuple[int, int, int, int]] = None,
                           case_sensitive: bool = False) -> Optional[Tuple[int, int]]:
        """
        通过OCR查找文本位置

        Args:
            text: 要查找的文本
            region: 搜索区域 (x, y, width, height)，None表示全屏
            case_sensitive: 是否区分大小写

        Returns:
            tuple: (x, y) 文本中心坐标，如果未找到返回None
        """
        try:
            screen_img = self.take_screenshot()

            if region:
                x, y, w, h = region
                screen_img = screen_img[y:y+h, x:x+w]

            # 统一解析
            detected_items = []  # [(text, cx, cy), ...]
            if self._use_predict:
                results = list(self.ocr_engine.predict(screen_img))
                if results and results[0]:
                    ocr_result = results[0]
                    for t, box in zip(ocr_result.get('rec_texts', []),
                                      ocr_result.get('rec_boxes', [])):
                        detected_items.append((t, int((box[0]+box[2])/2), int((box[1]+box[3])/2)))
            else:
                result = self.ocr_engine.ocr(screen_img, cls=True)
                if result and result[0]:
                    for line in result[0]:
                        box, (t, _) = line[0], line[1]
                        xs = [p[0] for p in box]; ys = [p[1] for p in box]
                        detected_items.append((t, int((min(xs)+max(xs))/2), int((min(ys)+max(ys))/2)))

            if not detected_items:
                logger.debug("PaddleOCR未识别到任何文本")
                return None

            search_text = text if case_sensitive else text.lower()

            for detected_text, cx, cy in detected_items:
                if not detected_text.strip():
                    continue

                compare_text = detected_text if case_sensitive else detected_text.lower()

                if search_text in compare_text:
                    center_x, center_y = cx, cy
                    if region:
                        center_x += region[0]
                        center_y += region[1]

                    logger.debug(f"OCR找到文本 '{text}' at ({center_x}, {center_y})")
                    return (center_x, center_y)

            logger.debug(f"OCR未找到文本: {text}")
            return None

        except Exception as e:
            logger.error(f"PaddleOCR识别失败: {e}")
            return None

    def scan_all_texts(self, region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict]:
        """
        一次性OCR扫描当前页面，返回所有识别到的文字及完整边界框信息

        与 find_element_by_ocr 不同，本方法返回页面上所有文字的详细信息，
        包括边界框坐标，适用于探索阶段一次性获取页面全部元素。

        Args:
            region: 搜索区域 (x, y, width, height)，None表示全屏

        Returns:
            list[dict]: 识别结果列表，每项包含:
                - text (str): 识别到的文字
                - cx (int): 文字中心x坐标（窗口内）
                - cy (int): 文字中心y坐标（窗口内）
                - bbox (tuple): 边界框 (x1, y1, x2, y2)，窗口内坐标
                - confidence (float): 识别置信度（2.x可用，3.x默认0.0）
        """
        try:
            screen_img = self.take_screenshot()

            if region:
                x, y, w, h = region
                screen_img = screen_img[y:y+h, x:x+w]

            items = []
            if self._use_predict:
                results = list(self.ocr_engine.predict(screen_img))
                if results and results[0]:
                    ocr_result = results[0]
                    for t, box in zip(ocr_result.get('rec_texts', []),
                                      ocr_result.get('rec_boxes', [])):
                        x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)
                        if region:
                            x1 += region[0]; y1 += region[1]
                            cx += region[0]; cy += region[1]
                            x2 += region[0]; y2 += region[1]
                        items.append({
                            'text': t,
                            'cx': cx,
                            'cy': cy,
                            'bbox': (x1, y1, x2, y2),
                            'confidence': 0.0,
                        })
            else:
                result = self.ocr_engine.ocr(screen_img, cls=True)
                if result and result[0]:
                    for line in result[0]:
                        box, (t, conf) = line[0], line[1]
                        xs = [p[0] for p in box]; ys = [p[1] for p in box]
                        x1, y1 = int(min(xs)), int(min(ys))
                        x2, y2 = int(max(xs)), int(max(ys))
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)
                        if region:
                            x1 += region[0]; y1 += region[1]
                            cx += region[0]; cy += region[1]
                            x2 += region[0]; y2 += region[1]
                        items.append({
                            'text': t,
                            'cx': cx,
                            'cy': cy,
                            'bbox': (x1, y1, x2, y2),
                            'confidence': float(conf),
                        })

            logger.debug(f"OCR扫描完成，识别到 {len(items)} 个文字项")
            return items

        except Exception as e:
            logger.error(f"OCR全量扫描失败: {e}")
            return []

    def extract_text_from_region(self, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        从指定区域提取所有文本

        Args:
            region: 提取区域 (x, y, width, height)，None表示全屏

        Returns:
            str: 提取的文本（按行拼接）
        """
        try:
            screen_img = self.take_screenshot()

            if region:
                x, y, w, h = region
                screen_img = screen_img[y:y+h, x:x+w]

            if self._use_predict:
                results = list(self.ocr_engine.predict(screen_img))
                if not results or not results[0]:
                    return ""
                rec_texts = results[0].get('rec_texts', [])
            else:
                result = self.ocr_engine.ocr(screen_img, cls=True)
                if not result or not result[0]:
                    return ""
                rec_texts = [line[1][0] for line in result[0]]

            all_text_lines = [t for t in rec_texts if t.strip()]

            return "\n".join(all_text_lines)

        except Exception as e:
            logger.error(f"文本提取失败: {e}")
            return ""

    def get_text_bounding_boxes(self, text: str, region: Optional[Tuple[int, int, int, int]] = None,
                               case_sensitive: bool = False) -> List[Dict]:
        """
        获取文本的边界框信息

        Args:
            text: 要查找的文本
            region: 搜索区域 (x, y, width, height)
            case_sensitive: 是否区分大小写

        Returns:
            list: 包含文本位置和边界框信息的列表
        """
        try:
            screen_img = self.take_screenshot()

            if region:
                x, y, w, h = region
                screen_img = screen_img[y:y+h, x:x+w]

            # 统一解析为 items: [(text, min_x, min_y, max_x, max_y), ...]
            items = []
            if self._use_predict:
                results = list(self.ocr_engine.predict(screen_img))
                if not results or not results[0]:
                    return []
                ocr_result = results[0]
                for t, box in zip(ocr_result.get('rec_texts', []),
                                  ocr_result.get('rec_boxes', [])):
                    items.append((t, box[0], box[1], box[2], box[3]))
            else:
                result = self.ocr_engine.ocr(screen_img, cls=True)
                if not result or not result[0]:
                    return []
                for line in result[0]:
                    box, (t, _) = line[0], line[1]
                    xs = [p[0] for p in box]; ys = [p[1] for p in box]
                    items.append((t, min(xs), min(ys), max(xs), max(ys)))

            search_text = text if case_sensitive else text.lower()
            results_list = []

            for detected_text, min_x, min_y, max_x, max_y in items:
                if not detected_text.strip():
                    continue

                compare_text = detected_text if case_sensitive else detected_text.lower()

                if search_text in compare_text:
                    width = max_x - min_x
                    height = max_y - min_y
                    center_x = int((min_x + max_x) / 2)
                    center_y = int((min_y + max_y) / 2)

                    if region:
                        min_x += region[0]
                        min_y += region[1]
                        center_x += region[0]
                        center_y += region[1]

                    result_dict = {
                        'text': detected_text,
                        'bbox': (min_x, min_y, width, height),
                        'center': (center_x, center_y),
                        'box': (min_x, min_y, max_x, max_y)
                    }
                    results_list.append(result_dict)

            return results_list

        except Exception as e:
            logger.error(f"获取文本边界框失败: {e}")
            return []


# 便捷函数
def aw_find_by_ocr(device_port: int, text: str, region: Optional[Tuple[int, int, int, int]] = None,
                   case_sensitive: bool = False) -> Optional[Tuple[int, int]]:
    """
    便捷方法：通过OCR查找文本位置

    Args:
        device_port: MuMu模拟器ADB端口
        text: 要查找的文本
        region: 搜索区域
        case_sensitive: 是否区分大小写

    Returns:
        tuple: (x, y) 文本中心坐标，如果未找到返回None
    """
    ocr_recog = OCRRecognition(device_port)
    return ocr_recog.find_element_by_ocr(text, region, case_sensitive)


def aw_scan_all_texts(device_port: int, region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict]:
    """
    便捷方法：一次性OCR扫描当前页面，返回所有文字及边界框信息

    Args:
        device_port: MuMu模拟器ADB端口
        region: 搜索区域

    Returns:
        list[dict]: 识别结果列表，每项含 text/cx/cy/bbox/confidence
    """
    ocr_recog = OCRRecognition(device_port)
    return ocr_recog.scan_all_texts(region)


def aw_extract_text(device_port: int, region: Optional[Tuple[int, int, int, int]] = None) -> str:
    """
    便捷方法：从指定区域提取所有文本

    Args:
        device_port: MuMu模拟器ADB端口
        region: 提取区域

    Returns:
        str: 提取的文本
    """
    ocr_recog = OCRRecognition(device_port)
    return ocr_recog.extract_text_from_region(region)


def aw_get_text_boxes(device_port: int, text: str, region: Optional[Tuple[int, int, int, int]] = None,
                     case_sensitive: bool = False) -> List[Dict]:
    """
    便捷方法：获取文本的边界框信息

    Args:
        device_port: MuMu模拟器ADB端口
        text: 要查找的文本
        region: 搜索区域
        case_sensitive: 是否区分大小写

    Returns:
        list: 包含文本位置和边界框信息的列表
    """
    ocr_recog = OCRRecognition(device_port)
    return ocr_recog.get_text_bounding_boxes(text, region, case_sensitive)