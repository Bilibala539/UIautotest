"""
统一AW基础操作模块

通过 PlatformDriver 抽象层实现一套代码兼容 MuMu 和 PC 两个平台。
所有 OCR、图像匹配、组合操作方法只维护一份。

核心方法:
  tap, input_text, find_text_by_ocr, find_image, ocr_scan_page
  click_text, click_image, text_exists, image_exists
  swipe, swipe_up, swipe_down, sleep ...
"""
import os
import base64

from image.image_name_mapping import MSG_UNREAD_ICON

# 禁用 mkldnn/oneDNN 以解决 PaddlePaddle 3.x PIR 兼容性问题
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['FLAGS_enable_pir_api'] = '0'
os.environ['FLAGS_enable_pir_in_executor'] = '0'
os.environ['MKLDNN_VERBOSE'] = '0'
os.environ['FLAGS_use_onednn'] = '0'

import logging
import time
from typing import Optional, Tuple
from datetime import datetime

import cv2
import numpy as np

from paddleocr import PaddleOCR

from utils.aw.driver.base_driver import BasePlatformDriver
from utils.aw.search_region import Normal

logger = logging.getLogger(__name__)

# 图片模板和截图目录
_BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
TEMPLATE_DIR = os.path.join(_BASE_DIR, 'image')
SCREENSHOT_DIR = os.path.join(_BASE_DIR, 'screenshots')
EXPLORER_SCREENSHOT_DIR = os.path.join(_BASE_DIR, 'explorer_output', 'screenshots')
EXPLORER_ELEMENTS_DIR = os.path.join(_BASE_DIR, 'explorer_output', 'elements')


class AWBase:
    """
    统一AW基础操作类

    通过 driver (BasePlatformDriver) 与底层平台交互，
    所有 OCR / 图像匹配 / 组合操作方法只维护一份。

    Args:
        driver: 平台驱动实例 (MuMuDriver 或 PCDriver)
    """

    TEMPLATE_DIR = TEMPLATE_DIR
    SCREENSHOT_DIR = SCREENSHOT_DIR
    EXPLORER_SCREENSHOT_DIR = EXPLORER_SCREENSHOT_DIR
    EXPLORER_ELEMENTS_DIR = EXPLORER_ELEMENTS_DIR

    # OCR 引擎单例（全局共享，避免重复加载模型）
    _ocr_engine: Optional[PaddleOCR] = None
    _ocr_use_predict: bool = False  # True = 3.x predict()，False = 2.x ocr()

    def __init__(self, driver: BasePlatformDriver):
        """
        初始化统一AW

        Args:
            driver: 平台驱动实例
        """
        self.driver = driver
        os.makedirs(self.TEMPLATE_DIR, exist_ok=True)
        os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)
        os.makedirs(self.EXPLORER_SCREENSHOT_DIR, exist_ok=True)
        os.makedirs(self.EXPLORER_ELEMENTS_DIR, exist_ok=True)

    @property
    def platform(self) -> str:
        """当前平台名称 ('mumu' 或 'pc')"""
        return self.driver.platform_name

    # ==================== OCR 引擎 ====================

    @classmethod
    def _get_ocr_engine(cls) -> PaddleOCR:
        """获取OCR引擎单例（自动检测 2.x / 3.x）"""
        if cls._ocr_engine is None:
            logger.info("🔧 初始化PaddleOCR引擎...")
            cls._ocr_engine = PaddleOCR(
                use_textline_orientation=False,
                use_doc_orientation_classify=False,
                text_detection_model_name='PP-OCRv5_mobile_det',
                text_recognition_model_name='PP-OCRv5_mobile_rec',
                enable_mkldnn=False,
            )
            # 运行时检测：有 predict 方法就是 3.x，否则是 2.x
            cls._ocr_use_predict = hasattr(cls._ocr_engine, 'predict')
            ver = "3.x (predict)" if cls._ocr_use_predict else "2.x (ocr)"
            logger.info(f"✅ PaddleOCR引擎初始化完成 — API: {ver}")
        return cls._ocr_engine

    # ==================== 截图 ====================

    # ==================== HTML 日志截图内嵌 ====================

    @staticmethod
    def _embed_screenshot_to_log(label: str, img_array: np.ndarray, screenshot_path: str) -> None:
        """
        将截图以 base64 内嵌到 HTML 日志文件中。

        Args:
            label:           显示在日志中的描述文字
            img_array:       BGR numpy 图像数组
            screenshot_path: 图片已保存的磁盘路径（仅用于展示）
        """
        # 从根 logger 的 handlers 里找到 HtmlFileHandler
        html_handler = None
        for h in logging.getLogger().handlers:
            if type(h).__name__ == 'HtmlFileHandler':
                html_handler = h
                break
        if html_handler is None:
            return

        try:
            success, buf = cv2.imencode('.png', img_array)
            if not success:
                return
            img_b64 = base64.b64encode(buf.tobytes()).decode('utf-8')
            html_handler.append_screenshot(label, screenshot_path, img_b64)
        except Exception as e:
            logger.debug(f"截图内嵌日志失败: {e}")

    # ==================== 截图 ====================

    def take_screenshot(self, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        截取目标窗口屏幕

        Args:
            save_path: 保存路径（可选）

        Returns:
            BGR 格式 numpy 数组，失败返回 None
        """
        img = self.driver.take_screenshot()
        if img is not None and save_path:
            # 使用 imencode + tofile 替代 imwrite，正确支持中文路径
            ext = os.path.splitext(save_path)[1] if os.path.splitext(save_path)[1] else '.png'
            success, buf = cv2.imencode(ext, img)
            if success:
                buf.tofile(save_path)
            logger.info(f"📸 截图已保存: {save_path}")
            # 内嵌到 HTML 日志
            self._embed_screenshot_to_log(f"📸 截图: {os.path.basename(save_path)}", img, save_path)
        return img

    def screenshot_for_explore(self, filename: str = None, subdir: str = None) -> str:
        """截取屏幕并保存到探索输出目录"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        if subdir:
            output_dir = os.path.join(self.EXPLORER_SCREENSHOT_DIR, subdir)
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = self.EXPLORER_SCREENSHOT_DIR

        output_path = os.path.join(output_dir, filename)
        self.take_screenshot(save_path=output_path)
        return output_path

    def crop_element(self, source_path: str, element_name: str,
                     x1: int, y1: int, x2: int, y2: int) -> Optional[str]:
        """从截图中裁切UI元素"""
        # 使用 imdecode + fromfile 替代 imread，正确支持中文路径
        img = cv2.imdecode(np.fromfile(source_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            logger.error(f"❌ 无法读取图片: {source_path}")
            return None

        height, width = img.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(width, x2), min(height, y2)

        if x2 <= x1 or y2 <= y1:
            logger.error(f"❌ 无效的裁切区域: ({x1},{y1},{x2},{y2})")
            return None

        cropped = img[y1:y2, x1:x2]
        output_path = os.path.join(self.EXPLORER_ELEMENTS_DIR, f"{element_name}.png")
        # 使用 imencode + tofile 替代 imwrite，正确支持中文路径
        success, buf = cv2.imencode('.png', cropped)
        if success:
            buf.tofile(output_path)
        logger.info(f"✂️ 元素已截取: {output_path}")
        return output_path

    # ==================== 点击 ====================

    def tap(self, x: int, y: int, dx: int = 0, dy: int = 0) -> bool:
        """
        点击窗口内坐标

        Args:
            x, y: 窗口内坐标
            dx, dy: 偏移量

        Returns:
            bool: 是否成功
        """
        target_x = x + dx
        target_y = y + dy
        screen_coords = self.driver.to_screen_coords(target_x, target_y)
        if not screen_coords:
            return False

        self.driver.tap(screen_coords[0], screen_coords[1])
        logger.info(f"👆 点击坐标 ({target_x}, {target_y})")
        self.sleep(0.3)
        return True

    def long_press(self, x: int, y: int, duration: float = 1.0,
                   dx: int = 0, dy: int = 0) -> bool:
        """
        长按窗口内坐标

        Args:
            x, y: 窗口内坐标
            duration: 长按持续时间（秒），默认1.0秒
            dx, dy: 偏移量

        Returns:
            bool: 是否成功
        """
        target_x = x + dx
        target_y = y + dy
        screen_coords = self.driver.to_screen_coords(target_x, target_y)
        if not screen_coords:
            return False

        self.driver.long_press(screen_coords[0], screen_coords[1], duration)
        logger.info(f"👆 长按坐标 ({target_x}, {target_y}), 时长={duration}s")
        self.sleep(0.5)
        return True

    def long_press_text(self, text: str, timeout: int = 10,
                        duration: float = 1.5,
                        region=Normal.ALL) -> bool:
        """
        OCR 找到文字后长按

        Args:
            text: 要查找的文字
            timeout: 超时时间（秒）
            duration: 长按持续时间（秒）
            region: 搜索区域

        Returns:
            bool: 是否成功
        """
        time.sleep(1)
        pos = self.find_text_by_ocr(text, timeout=timeout, region=region)
        assert pos is not None, f"未找到文字 '{text}'"

        bl = self.long_press(pos[0], pos[1], duration=duration)
        logger.info(f"长按文字 '{text}' 位置：({pos[0]}, {pos[1]})")
        return bl

    def long_press_image(self, image: str, threshold: float = 0.8,
                         timeout: int = 10, duration: float = 1.0,
                         region=Normal.ALL) -> bool:
        """
        模板匹配找到图片后长按

        Args:
            image: 模板图片文件名或绝对路径
            threshold: 匹配阈值
            timeout: 超时时间（秒）
            duration: 长按持续时间（秒）
            region: 搜索区域

        Returns:
            bool: 是否成功
        """
        pos = self.find_image(image, threshold=threshold, timeout=timeout, region=region)
        assert pos is not None, f"未找到图片 '{image}'"
        return self.long_press(pos[0], pos[1], duration)

    # ==================== 输入 ====================

    def input_text(self, text: str) -> bool:
        """
        输入文字（平台自动适配输入方式）

        Args:
            text: 要输入的文字

        Returns:
            bool: 是否成功
        """
        result = self.driver.input_text(text)
        self.sleep(0.3)
        return result

    def clear_input(self) -> bool:
        """清空当前输入框"""
        return self.driver.clear_input()

    # ==================== 按键 ====================

    def press_key(self, key: str) -> bool:
        """按下指定按键"""
        result = self.driver.press_key(key)
        self.sleep(0.2)
        return result

    def press_back(self) -> bool:
        """按下返回键 (Escape)"""
        logger.info("🔙 按返回键")
        return self.press_key('escape')

    def press_home(self) -> bool:
        """按下Home键"""
        logger.info("🏠 按Home键")
        self.sleep(0.3)
        return True

    def select_all(self) -> bool:
        """
        全选当前输入框内容 (Ctrl+A)

        通过 pyautogui.hotkey 发送 Ctrl+A 热键，在 MuMu 模拟器中触发全选操作。

        Returns:
            bool: 操作是否成功
        """
        import pyautogui
        pyautogui.hotkey('ctrl', 'a')
        logger.info("📋 全选文本 (Ctrl+A)")
        self.sleep(0.3)
        return True

    # ==================== OCR 文字识别 ====================

    def _ocr_raw(self, img: np.ndarray, region=None) -> list:
        """
        底层 OCR 识别，返回统一格式的识别结果列表

        将 PaddleOCR 2.x / 3.x 的不同输出格式统一为:
        [{"text": str, "cx": int, "cy": int, "bbox": (x1,y1,x2,y2), "confidence": float}, ...]

        坐标已转换为窗口内绝对坐标（已加上 region 偏移）。

        Args:
            img: 全屏截图 (BGR numpy 数组)
            region: 搜索区域 (x, y, w, h)，None 表示全屏

        Returns:
            list[dict]: 统一格式的 OCR 识别结果
        """
        ocr = self._get_ocr_engine()

        dx, dy = 0, 0
        search_img = img
        if region:
            rx, ry, rw, rh = region
            search_img = img[ry:ry + rh, rx:rx + rw]
            dx, dy = rx, ry

        items = []
        if self._ocr_use_predict:
            # PaddleOCR 3.x: predict() → 生成器，含 rec_texts / rec_boxes
            results = list(ocr.predict(search_img))
            if results and results[0]:
                ocr_result = results[0]
                for t, box in zip(ocr_result.get('rec_texts', []),
                                  ocr_result.get('rec_boxes', [])):
                    x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                    items.append({
                        'text': t,
                        'cx': int((x1 + x2) / 2) + dx,
                        'cy': int((y1 + y2) / 2) + dy,
                        'bbox': (x1 + dx, y1 + dy, x2 + dx, y2 + dy),
                        'confidence': 0.0,
                    })
        else:
            # PaddleOCR 2.x: ocr() → [[line, ...]]，line=[box4pts, (text,conf)]
            results = ocr.ocr(search_img, cls=True)
            if results and results[0]:
                for line in results[0]:
                    box, (t, conf) = line[0], line[1]
                    xs = [p[0] for p in box]
                    ys = [p[1] for p in box]
                    x1, y1 = int(min(xs)), int(min(ys))
                    x2, y2 = int(max(xs)), int(max(ys))
                    items.append({
                        'text': t,
                        'cx': int((x1 + x2) / 2) + dx,
                        'cy': int((y1 + y2) / 2) + dy,
                        'bbox': (x1 + dx, y1 + dy, x2 + dx, y2 + dy),
                        'confidence': float(conf),
                    })

        return items

    def ocr_scan_page(self, region=Normal.ALL) -> list:
        """
        一次性 OCR 全量扫描当前页面，返回所有文字及完整边界框信息

        探索阶段推荐使用此方法替代多次 find_text_by_ocr()，一次截图+OCR
        即可获取页面全部文字元素，大幅提升探索效率。

        Args:
            region: 搜索区域 (x, y, w, h)，默认全屏

        Returns:
            list[dict]: 识别结果列表，每项包含:
                - text (str): 识别到的文字
                - cx (int): 文字中心x坐标（窗口内）
                - cy (int): 文字中心y坐标（窗口内）
                - bbox (tuple): 边界框 (x1, y1, x2, y2)，窗口内坐标
                - confidence (float): 识别置信度

        示例:
            # 扫描页面全部文字
            items = aw.ocr_scan_page()
            for item in items:
                print(f"{item['text']} @ ({item['cx']}, {item['cy']}) bbox={item['bbox']}")

            # 在扫描结果中查找特定文字
            target = next((i for i in items if '设置' in i['text']), None)
            if target:
                aw.tap(target['cx'], target['cy'])
        """
        img = self.take_screenshot()
        if img is None:
            logger.warning("⚠️ ocr_scan_page: 截图失败")
            return []

        items = self._ocr_raw(img, region=region)

        if items:
            texts = [item['text'] for item in items]
            logger.info(f"📝 OCR全量扫描: 识别到 {len(items)} 个文字项 — {texts}")
        else:
            logger.info("📝 OCR全量扫描: 未识别到任何文字")

        return items

    def find_text_by_ocr(self, text: str, timeout: int = 10,
                         region=Normal.ALL,
                         case_sensitive: bool = False) -> Optional[Tuple[int, int]]:
        """
        OCR 找文字，返回文字中心的窗口内坐标

        Args:
            text: 要查找的文字
            timeout: 超时时间（秒）
            region: 搜索区域 (x, y, w, h)
            case_sensitive: 是否区分大小写

        Returns:
            文字中心坐标 (窗口内)，未找到返回 None
        """
        end_time = time.time() + timeout

        while time.time() < end_time:
            img = self.take_screenshot()
            if img is None:
                self.sleep(0.5)
                continue

            items = self._ocr_raw(img, region=region)

            if items:
                rec_texts = [item['text'] for item in items]
                logger.info(f"📝 OCR识别到的文字: {rec_texts}")

                for item in items:
                    detected_text = item['text']
                    if not detected_text.strip():
                        continue

                    if case_sensitive:
                        match = text in detected_text
                    else:
                        match = text.lower() in detected_text.lower()

                    if match:
                        center_x, center_y = item['cx'], item['cy']
                        logger.info(f"🔍 找到文字 '{text}' @ ({center_x}, {center_y})")
                        return center_x, center_y

            self.sleep(0.5)
            break

        # 失败时仅记录日志，不保存截图文件（用例失败时由 conftest 统一截图）
        logger.warning(f"⚠️ 未找到文字 '{text}'")

        return None

    def text_exists(self, text: str, timeout: int = 5,
                    region=Normal.ALL):
        """检查文字是否存在"""
        pos = self.find_text_by_ocr(text, timeout=timeout, region=region)
        if pos is not None:
            return pos
        else:
            assert False

    # ==================== 图像模板匹配 ====================

    def find_image(self, template_name: str, threshold: float = 0.8,
                   timeout: int = 10,
                   region=Normal.ALL) -> Optional[Tuple[int, int]]:
        """
        模板匹配找图，返回图片中心的窗口内坐标

        Args:
            template_name: 模板图片文件名或绝对路径
            threshold: 匹配阈值 0~1
            timeout: 超时时间（秒）
            region: 搜索区域 (x, y, w, h)，有 region 时只截取该区域截图

        Returns:
            图片中心坐标 (窗口内)，未找到返回 None
        """
        template_path = template_name if os.path.isabs(template_name) \
            else os.path.join(self.TEMPLATE_DIR, template_name)

        if not os.path.exists(template_path):
            logger.error(f"❌ 模板图片不存在: {template_path}")
            assert None

        template = cv2.imdecode(np.fromfile(template_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if template is None:
            logger.error(f"❌ 无法读取模板图片: {template_path}")
            assert None

        template_h, template_w = template.shape[:2]
        end_time = time.time() + timeout

        # ADB 模式截图与 pyautogui 截图存在细微色差，通过 driver 的阈值偏移补偿
        effective_threshold = threshold + getattr(self.driver, 'threshold_offset', 0.0)

        while time.time() < end_time:
            # 有 region 时只截取该区域，减少截图处理范围；无 region 时截全屏
            if region:
                rx, ry, rw, rh = region
                full_img = self.take_screenshot()
                if full_img is None:
                    self.sleep(0.5)
                    continue
                search_img = full_img[ry:ry + rh, rx:rx + rw]
                dx, dy = rx, ry
            else:
                search_img = self.take_screenshot()
                if search_img is None:
                    self.sleep(0.5)
                    continue
                dx, dy = 0, 0

            result = cv2.matchTemplate(search_img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= effective_threshold:
                center_x = max_loc[0] + template_w // 2 + dx
                center_y = max_loc[1] + template_h // 2 + dy
                logger.info(f"🖼️ 找到图片 '{template_name}' @ ({center_x}, {center_y}), score={max_val:.2f}")
                return (center_x, center_y)

            self.sleep(0.5)

        # 超时时仅记录日志，不保存截图文件（用例失败时由 conftest 统一截图）
        logger.warning(f"⚠️ 未找到图片 '{template_name}'")
        return None

    def image_exists(self, template_name: str, threshold: float = 0.8,
                     timeout: int = 5,
                     region=Normal.ALL) -> bool:
        """断言图片必须存在（找不到则 assert 失败）"""
        pos = self.find_image(template_name, threshold=threshold, timeout=timeout,
                              region=region)
        assert pos is not None, f"断言失败: 未找到图片 '{template_name}'"
        return True

    # ==================== 组合操作 ====================

    def click_text(self, text: str, timeout: int = 10,
                   dx: int = 0, dy: int = 0,
                   region=Normal.ALL):
        """OCR 找到文字后点击"""
        pos = self.text_exists(text, timeout=timeout, region=region)
        if pos:
            return self.tap(pos[0], pos[1], dx, dy)
        return False

    def click_image(self, image: str, threshold: float = 0.8,
                    timeout: int = 10, dx: int = 0, dy: int = 0,
                    region=Normal.ALL):
        """模板匹配找到图片后点击"""
        pos = self.find_image(image, threshold=threshold, timeout=timeout, region=region)
        assert pos is not None, f"点击图片失败: 未找到 '{image}'"
        return self.tap(pos[0], pos[1], dx, dy)

    # ==================== 滑动 ====================

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration: float = 0.3) -> bool:
        """从起点滑动到终点（窗口内坐标）"""
        start_coords = self.driver.to_screen_coords(start_x, start_y)
        end_coords = self.driver.to_screen_coords(end_x, end_y)
        if not start_coords or not end_coords:
            return False

        result = self.driver.swipe(start_coords[0], start_coords[1],
                                   end_coords[0], end_coords[1], duration)
        logger.info(f"👆 滑动 ({start_x},{start_y}) → ({end_x},{end_y})")
        self.sleep(0.3)
        return result

    def swipe_up(self, distance: int = 400) -> bool:
        """向上滑动"""
        return self.swipe(270, 700, 270, 700 - distance)

    def swipe_down(self, distance: int = 400) -> bool:
        """向下滑动"""
        return self.swipe(270, 300, 270, 300 + distance)

    def swipe_left(self, start_coords, distance: int = 300) -> bool:
        """向左滑动"""
        return self.swipe(start_coords[0], start_coords[1], (start_coords[0] - distance), start_coords[1])

    def swipe_right(self, distance: int = 300) -> bool:
        """向右滑动"""
        return self.swipe(100, 500, 100 + distance, 500)

    def scroll_up(self, clicks: int = 5) -> bool:
        """向上滚动（鼠标滚轮）"""
        rect = self.driver.get_window_rect()
        if not rect:
            return False
        left, top, w, h = rect
        return self.driver.scroll(left + w // 2, top + h // 2, clicks)

    def scroll_down(self, clicks: int = 5) -> bool:
        """向下滚动（鼠标滚轮）"""
        return self.scroll_up(-clicks)

    # ==================== 开关操作 ====================

    def is_switch_on(self, switch_text: str, region=Normal.ALL) -> bool:
        """
        检测页面中指定开关的当前状态（通用方法）

        通过OCR定位开关文字的y坐标，然后扫描该行右侧区域
        是否存在蓝色像素来判断开关是否开启。

        开关UI特征:
        - 开启状态: 蓝色 BGR≈(255,143,47)
        - 关闭状态: 浅灰色（与白色背景几乎一致）
        - 开关x位置: 约 x=460~520（532宽度）或 x=470~530（540宽度）
        - 检测方式: 扫描开关文字y坐标±25px范围内x=420~530区域的蓝色像素

        Args:
            switch_text: 开关标题文字（如 "连续播放语音消息"）
            region: 搜索区域

        Returns:
            bool: True=开启(蓝色), False=关闭
        """
        # 1. OCR定位开关文字，获取y坐标
        pos = self.find_text_by_ocr(switch_text, timeout=3, region=region)
        assert pos is not None, f"未找到开关文字 '{switch_text}'"
        text_y = pos[1]

        # 2. 截图并扫描开关区域的蓝色像素
        img = self.take_screenshot()
        assert img is not None, "截图失败"

        # 开关区域: x=420~530, y=text_y-25 ~ text_y+25
        # 适配 532/540 两种分辨率宽度
        img_w = img.shape[1]
        scan_x1 = 420
        scan_x2 = min(img_w, 530)
        scan_y1 = max(0, text_y - 25)
        scan_y2 = min(img.shape[0], text_y + 25)

        switch_region = img[scan_y1:scan_y2, scan_x1:scan_x2]

        # 3. 检测蓝色像素 (BGR格式: B>200, G在100~180, R<100)
        b, g, r = switch_region[:, :, 0], switch_region[:, :, 1], switch_region[:, :, 2]
        blue_mask = (b > 200) & (g > 100) & (g < 180) & (r < 100)
        blue_pixel_count = int(np.sum(blue_mask))

        # 蓝色像素超过阈值认为开关开启
        is_on = blue_pixel_count > 50
        state_text = "开启" if is_on else "关闭"
        logger.info(f"🔍 开关 '{switch_text}' 状态: {state_text} (蓝色像素: {blue_pixel_count})")
        return is_on

    def toggle_switch(self, switch_text: str, target_state: bool,
                      region=Normal.ALL) -> bool:
        """
        切换页面中指定开关到目标状态（通用方法）

        先检测当前状态，如果与目标不一致则点击开关文字右侧的开关区域进行切换，
        然后再次检测确认切换成功。

        Args:
            switch_text: 开关标题文字
            target_state: 目标状态 True=开启, False=关闭
            region: 搜索区域

        Returns:
            bool: 是否成功切换到目标状态
        """
        current_state = self.is_switch_on(switch_text, region=region)

        if current_state == target_state:
            state_text = "开启" if target_state else "关闭"
            logger.info(f"✅ 开关 '{switch_text}' 已是{state_text}状态，无需切换")
            return True

        # 点击开关区域（页面右侧的 toggle 控件）
        pos = self.find_text_by_ocr(switch_text, timeout=3, region=region)
        assert pos is not None, f"未找到开关文字 '{switch_text}'"
        # 通过扫描文字行右侧找到开关控件的精确 x 位置
        img = self.take_screenshot()
        img_w = img.shape[1] if img is not None else 540
        text_y = pos[1]
        # 扫描文字行 (y±8) 右侧 (x从img_w-120到img_w) 的非白色像素
        scan_y1 = max(0, text_y - 8)
        scan_y2 = min(img.shape[0], text_y + 8)
        scan_x1 = img_w - 120
        row_strip = img[scan_y1:scan_y2, scan_x1:img_w]
        # 找非白色像素 (开关控件的灰色或蓝色)
        non_white = (row_strip[:, :, 0].astype(int) < 245) | \
                    (row_strip[:, :, 1].astype(int) < 245) | \
                    (row_strip[:, :, 2].astype(int) < 245)
        nw_x = np.where(non_white.any(axis=0))[0]
        if len(nw_x) > 3:
            # 取非白色像素的中心 x
            tap_x = scan_x1 + int(nw_x.mean())
        else:
            # 兜底：使用经验值
            tap_x = img_w - 40
        logger.info(f"🔘 点击开关: img_w={img_w}, tap=({tap_x}, {text_y})")
        self.tap(tap_x, text_y)
        self.sleep(1.0)

        # 验证切换结果
        new_state = self.is_switch_on(switch_text, region=region)
        state_text = "开启" if target_state else "关闭"
        if new_state == target_state:
            logger.info(f"✅ 开关 '{switch_text}' 已成功切换为{state_text}")
            return True
        else:
            logger.warning(f"⚠️ 开关 '{switch_text}' 切换到{state_text}失败")
            return False

    # ==================== 工具方法 ====================

    @staticmethod
    def random_digits(length: int = 10) -> str:
        """
        生成指定长度的随机数字字符串

        Args:
            length: 字符串长度，默认10位

        Returns:
            str: 由0-9随机数字组成的字符串
        """
        import random
        return ''.join(random.choices('0123456789', k=length))

    def sleep(self, seconds: float) -> None:
        """等待指定时间"""
        time.sleep(seconds)

    # ==================== 探索方法 ====================

    def explore_page(self, page_name: str) -> dict:
        """
        探索当前页面，截图并全量扫描页面元素

        一次性完成截图 + OCR 全量扫描，返回页面全部文字元素及其边界框信息。
        探索阶段推荐直接使用此方法，避免多次调用 find_text_by_ocr()。

        Args:
            page_name: 页面名称（用于截图文件命名）

        Returns:
            dict: 页面探索结果，包含:
                - name (str): 页面名称
                - screenshot (str): 截图文件路径
                - timestamp (str): 探索时间
                - ocr_items (list[dict]): OCR 全量扫描结果，每项含 text/cx/cy/bbox/confidence
        """
        logger.info(f"📱 开始探索页面: {page_name}")
        screenshot_path = self.screenshot_for_explore(f"{page_name}.png")
        ocr_items = self.ocr_scan_page()
        page_info = {
            "name": page_name,
            "screenshot": screenshot_path,
            "timestamp": datetime.now().isoformat(),
            "ocr_items": ocr_items,
        }
        logger.info(f"✅ 页面探索完成: {page_name}，识别到 {len(ocr_items)} 个文字项")
        return page_info

    def explore_flow(self, flow_name: str, steps: list) -> list:
        """探索操作流程"""
        logger.info(f"🔄 开始探索流程: {flow_name}")
        results = []

        for i, step in enumerate(steps, 1):
            action = step.get("action")
            desc = step.get("desc", "")
            logger.info(f"步骤 {i}: {desc}")
            result = {"step": i, "action": action, "desc": desc}

            if action == "tap":
                self.tap(step["x"], step["y"])
            elif action == "swipe":
                self.swipe(step["x1"], step["y1"], step["x2"], step["y2"])
            elif action == "swipe_up":
                self.swipe_up()
            elif action == "swipe_down":
                self.swipe_down()
            elif action == "back":
                self.press_back()
            elif action == "screenshot":
                path = self.screenshot_for_explore(step.get("name"))
                result["screenshot"] = path
            elif action == "wait":
                self.sleep(step.get("time", 1))
            elif action == "input":
                self.input_text(step.get("text", ""))
            elif action == "click_text":
                self.click_text(step.get("text", ""))

            results.append(result)

        logger.info(f"✅ 流程探索完成: {flow_name}")
        return results
