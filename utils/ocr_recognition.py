"""
OCR文字识别工具模块
提供基于PaddleOCR的文本定位功能
"""

import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from typing import Optional, Tuple, List, Dict
import logging

# 使用PaddleOCR替代pytesseract
try:
    from paddleocr import PaddleOCR
except ImportError:
    raise ImportError("PaddleOCR未安装，请运行: pip install paddleocr>=2.6.0")

logger = logging.getLogger(__name__)

class OCRRecognition:
    """OCR文字识别工具类"""

    def __init__(self, driver, lang: str = "ch", use_gpu: bool = False,
                 det_db_box_thresh: float = 0.5, det_db_unclip_ratio: float = 1.6):
        """
        初始化OCR识别工具

        Args:
            driver: Appium WebDriver实例
            lang: OCR语言配置 ("ch" 中文, "en" 英文, "fr" 法语等)
            use_gpu: 是否使用GPU加速
            det_db_box_thresh: 检测框阈值
            det_db_unclip_ratio: 检测框扩展比例
        """
        self.driver = driver
        self.lang = lang
        self.use_gpu = use_gpu

        # 初始化PaddleOCR引擎（只初始化一次）
        self.ocr_engine = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
            use_gpu=use_gpu,
            det_db_box_thresh=det_db_box_thresh,
            det_db_unclip_ratio=det_db_unclip_ratio,
            show_log=False  # 关闭PaddleOCR内部日志，避免干扰
        )

    def take_screenshot(self) -> np.ndarray:
        """
        截取当前屏幕

        Returns:
            numpy.ndarray: 屏幕截图的numpy数组 (RGB格式)
        """
        try:
            screenshot = self.driver.get_screenshot_as_png()
            image = Image.open(BytesIO(screenshot))
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

            # PaddleOCR直接处理numpy数组
            result = self.ocr_engine.ocr(screen_img, cls=True)

            if not result or not result[0]:
                logger.debug("PaddleOCR未识别到任何文本")
                return None

            search_text = text if case_sensitive else text.lower()

            for line in result[0]:
                # line结构: [[[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], ('text', confidence)]]
                detected_text = line[1][0]
                confidence = line[1][1]

                if not detected_text.strip():
                    continue

                compare_text = detected_text if case_sensitive else detected_text.lower()

                if search_text in compare_text:
                    # 计算文本框中心点
                    box_points = line[0]  # 四个角点坐标
                    x_coords = [point[0] for point in box_points]
                    y_coords = [point[1] for point in box_points]
                    center_x = int(sum(x_coords) / 4)
                    center_y = int(sum(y_coords) / 4)

                    # 如果指定了搜索区域，需要将相对坐标转换为绝对坐标
                    if region:
                        center_x += region[0]
                        center_y += region[1]

                    logger.debug(f"OCR找到文本 '{text}' at ({center_x}, {center_y}), confidence: {confidence:.2f}")
                    return (center_x, center_y)

            logger.debug(f"OCR未找到文本: {text}")
            return None

        except Exception as e:
            logger.error(f"PaddleOCR识别失败: {e}")
            return None

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

            result = self.ocr_engine.ocr(screen_img, cls=True)

            if not result or not result[0]:
                return ""

            # 提取所有识别到的文本
            all_text_lines = []
            for line in result[0]:
                detected_text = line[1][0]
                if detected_text.strip():
                    all_text_lines.append(detected_text)

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

            result = self.ocr_engine.ocr(screen_img, cls=True)

            if not result or not result[0]:
                return []

            search_text = text if case_sensitive else text.lower()
            results_list = []

            for line in result[0]:
                detected_text = line[1][0]
                confidence = line[1][1]
                box_points = line[0]

                if not detected_text.strip():
                    continue

                compare_text = detected_text if case_sensitive else detected_text.lower()

                if search_text in compare_text:
                    # 计算边界框（最小外接矩形）
                    x_coords = [point[0] for point in box_points]
                    y_coords = [point[1] for point in box_points]
                    min_x, max_x = min(x_coords), max(x_coords)
                    min_y, max_y = min(y_coords), max(y_coords)
                    width = max_x - min_x
                    height = max_y - min_y

                    center_x = int((min_x + max_x) / 2)
                    center_y = int((min_y + max_y) / 2)

                    # 如果指定了搜索区域，需要将相对坐标转换为绝对坐标
                    if region:
                        min_x += region[0]
                        min_y += region[1]
                        center_x += region[0]
                        center_y += region[1]

                    result_dict = {
                        'text': detected_text,
                        'bbox': (min_x, min_y, width, height),
                        'center': (center_x, center_y),
                        'confidence': confidence,
                        'box_points': box_points  # 原始四点坐标
                    }
                    results_list.append(result_dict)

            return results_list

        except Exception as e:
            logger.error(f"获取文本边界框失败: {e}")
            return []

# 便捷函数
def aw_find_by_ocr(driver, text: str, region: Optional[Tuple[int, int, int, int]] = None,
                   case_sensitive: bool = False) -> Optional[Tuple[int, int]]:
    """
    便捷方法：通过OCR查找文本位置

    Args:
        driver: Appium WebDriver实例
        text: 要查找的文本
        region: 搜索区域
        case_sensitive: 是否区分大小写

    Returns:
        tuple: (x, y) 文本中心坐标，如果未找到返回None
    """
    ocr_recog = OCRRecognition(driver)
    return ocr_recog.find_element_by_ocr(text, region, case_sensitive)

def aw_extract_text(driver, region: Optional[Tuple[int, int, int, int]] = None) -> str:
    """
    便捷方法：从指定区域提取所有文本

    Args:
        driver: Appium WebDriver实例
        region: 提取区域

    Returns:
        str: 提取的文本
    """
    ocr_recog = OCRRecognition(driver)
    return ocr_recog.extract_text_from_region(region)

def aw_get_text_boxes(driver, text: str, region: Optional[Tuple[int, int, int, int]] = None,
                     case_sensitive: bool = False) -> List[Dict]:
    """
    便捷方法：获取文本的边界框信息

    Args:
        driver: Appium WebDriver实例
        text: 要查找的文本
        region: 搜索区域
        case_sensitive: 是否区分大小写

    Returns:
        list: 包含文本位置和边界框信息的列表
    """
    ocr_recog = OCRRecognition(driver)
    return ocr_recog.get_text_bounding_boxes(text, region, case_sensitive)