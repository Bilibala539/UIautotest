"""
统一AW基础操作模块

通过 PlatformDriver 抽象层实现一套代码兼容 MuMu 和 PC 两个平台。
所有 OCR、图像匹配、组合操作方法只维护一份。

核心方法:
  tap, input_text, find_text_by_ocr, find_image
  click_text, click_image, text_exists, image_exists
  swipe, swipe_up, swipe_down, sleep ...
"""
import os

# 禁用 mkldnn/oneDNN 以解决 PaddlePaddle 3.x 兼容性问题
os.environ['FLAGS_use_mkldnn'] = '0'

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
        """获取OCR引擎单例"""
        if cls._ocr_engine is None:
            logger.info("🔧 初始化PaddleOCR引擎...")
            cls._ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang='ch',
                show_log=False,
            )
            logger.info("✅ PaddleOCR引擎初始化完成")
        return cls._ocr_engine

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
        pos = self.find_text_by_ocr(text, timeout=timeout, region=region)
        assert pos is not None, f"未找到文字 '{text}'"
        return self.long_press(pos[0], pos[1], duration)

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

    # ==================== OCR 文字识别 ====================

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
        ocr = self._get_ocr_engine()
        end_time = time.time() + timeout

        while time.time() < end_time:
            img = self.take_screenshot()
            if img is None:
                self.sleep(0.5)
                continue

            dx, dy = 0, 0
            search_img = img
            if region:
                rx, ry, rw, rh = region
                search_img = img[ry:ry + rh, rx:rx + rw]
                dx, dy = rx, ry

            results = ocr.ocr(search_img, cls=True)
            if results and results[0]:
                all_texts = [line[1][0] for line in results[0]]
                logger.info(f"📝 OCR识别到的文字: {all_texts}")

                for line in results[0]:
                    detected_text = line[1][0]
                    if case_sensitive:
                        match = text in detected_text
                    else:
                        match = text.lower() in detected_text.lower()

                    if match:
                        box = line[0]
                        center_x = int((box[0][0] + box[2][0]) / 2) + dx
                        center_y = int((box[0][1] + box[2][1]) / 2) + dy
                        logger.info(f"🔍 找到文字 '{text}' @ ({center_x}, {center_y})")
                        return center_x, center_y

            self.sleep(0.5)
            break

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
            region: 搜索区域 (x, y, w, h)

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

        while time.time() < end_time:
            img = self.take_screenshot()
            if img is None:
                self.sleep(0.5)
                continue

            dx, dy = 0, 0
            search_img = img
            if region:
                rx, ry, rw, rh = region
                search_img = img[ry:ry + rh, rx:rx + rw]
                dx, dy = rx, ry

            result = cv2.matchTemplate(search_img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                center_x = max_loc[0] + template_w // 2 + dx
                center_y = max_loc[1] + template_h // 2 + dy
                logger.info(f"🖼️ 找到图片 '{template_name}' @ ({center_x}, {center_y}), score={max_val:.2f}")
                return (center_x, center_y)

            self.sleep(0.5)

        # 超时截图保存以便调试
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        template_basename = os.path.basename(template_name).split('.')[0]
        screenshot_name = f"failed_find_{template_basename}_{timestamp}.png"
        screenshot_path = os.path.join(self.SCREENSHOT_DIR, screenshot_name)
        self.take_screenshot(save_path=screenshot_path)
        logger.warning(f"⚠️ 未找到图片 '{template_name}'，已保存截图: {screenshot_path}")
        assert False

    def image_exists(self, template_name: str, threshold: float = 0.8,
                     timeout: int = 5,
                     region=Normal.ALL) -> bool:
        """检查图片是否存在"""
        return self.find_image(template_name, threshold=threshold, timeout=timeout,
                               region=region) is not None

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
        if pos:
            return self.tap(pos[0], pos[1], dx, dy)
        assert False, "点击图片失败"

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
        """探索当前页面，截图并记录基本信息"""
        logger.info(f"📱 开始探索页面: {page_name}")
        screenshot_path = self.screenshot_for_explore(f"{page_name}.png")
        page_info = {
            "name": page_name,
            "screenshot": screenshot_path,
            "timestamp": datetime.now().isoformat(),
            "elements": []
        }
        logger.info(f"✅ 页面探索完成: {page_name}")
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
