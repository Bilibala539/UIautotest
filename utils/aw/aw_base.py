"""
AW基础操作模块 - 合并自aw_base和aw_action
基于pyautogui实现窗口操作，集成OCR和图像识别

核心方法:
- tap: 点击坐标区域（支持偏移量）
- input_text: 输入文本
- find_text_by_ocr: OCR找文字，返回坐标
- find_image: 找图片，返回坐标
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

import pyautogui

from utils.aw.search_region import Normal

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

from paddleocr import PaddleOCR

from utils.window_manager import WindowManager, WindowRect, get_mumu_window_rect

logger = logging.getLogger(__name__)


class AWBase:
    """
    AW基础操作类

    核心方法:
    - tap(x, y, dx, dy): 点击坐标区域
    - input_text(text): 输入文本
    - find_text_by_ocr(text): OCR找文字，返回坐标
    - find_image(template_name): 找图片，返回坐标
    """

    TEMPLATE_DIR = r"E:\UIAutotest\templates"
    SCREENSHOT_DIR = r"E:\UIAutotest\screenshots"
    EXPLORER_SCREENSHOT_DIR = r"E:\UIAutotest\explorer_output\screenshots"
    EXPLORER_ELEMENTS_DIR = r"E:\UIAutotest\explorer_output\elements"
    _ocr_engine: Optional[PaddleOCR] = None

    def __init__(self, instance_id: int):
        """
        初始化

        Args:
            instance_id: MuMu模拟器实例ID (0, 1, 2...)
        """
        self.instance_id = instance_id
        self._window_rect: Optional[WindowRect] = None
        os.makedirs(self.TEMPLATE_DIR, exist_ok=True)
        os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)
        os.makedirs(self.EXPLORER_SCREENSHOT_DIR, exist_ok=True)
        os.makedirs(self.EXPLORER_ELEMENTS_DIR, exist_ok=True)

    @classmethod
    def _get_ocr_engine(cls) -> PaddleOCR:
        """获取OCR引擎单例"""
        if cls._ocr_engine is None:
            logger.info("🔧 初始化PaddleOCR引擎...")
            cls._ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang='ch',
                enable_mkldnn=False,  # 禁用 mkldnn 以解决兼容性问题
                use_gpu=False
            )
            logger.info("✅ PaddleOCR引擎初始化完成")
        return cls._ocr_engine

    # ==================== 窗口操作 ====================

    # 获取MuMu模拟器窗口区域
    def _get_window_rect(self, refresh: bool = False) -> Optional[WindowRect]:
        """获取窗口区域"""
        if refresh or self._window_rect is None:
            self._window_rect = get_mumu_window_rect(self.instance_id)
        return self._window_rect

    # 将窗口内坐标转换为屏幕绝对坐标
    def _to_screen_coords(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """将窗口内坐标转换为屏幕坐标"""
        rect = self._get_window_rect()
        if rect:
            return rect.to_absolute(x, y)
        logger.error(f"❌ 无法获取窗口区域，实例ID: {self.instance_id}")
        return None

    # 将MuMu模拟器窗口置于前台
    def _focus_window(self) -> bool:
        """将窗口置于前台"""
        return WindowManager.focus_window(self.instance_id)

    # ==================== 截图操作 ====================

    # 截取MuMu模拟器窗口屏幕，返回BGR格式的numpy数组
    def take_screenshot(self, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        截取窗口屏幕

        Args:
            save_path: 保存路径

        Returns:
            Optional[np.ndarray]: 截图图像(BGR格式)
        """
        rect = self._get_window_rect(refresh=True)
        if not rect:
            logger.error("❌ 无法获取窗口区域进行截图")
            return None

        try:
            screenshot = pyautogui.screenshot(region=rect.region)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            if save_path:
                cv2.imwrite(save_path, img)
                logger.info(f"📸 截图已保存: {save_path}")
            return img
        except Exception as e:
            logger.error(f"❌ 截图失败: {e}")
            return None

    # 截图并保存到探索输出目录，用于功能探索
    def screenshot_for_explore(self, filename: str = None, subdir: str = None) -> str:
        """
        截取屏幕并保存到探索目录

        Args:
            filename: 文件名，不填则自动生成时间戳名称
            subdir: 子目录名（在screenshots下），不填则直接保存到screenshots

        Returns:
            str: 保存的文件路径
        """
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

    # 从截图中裁切UI元素并保存到elements目录
    def crop_element(self, source_path: str, element_name: str,
                     x1: int, y1: int, x2: int, y2: int) -> Optional[str]:
        """
        从截图中裁切元素

        Args:
            source_path: 源截图路径
            element_name: 元素名称（不含.png后缀）
            x1, y1, x2, y2: 裁切区域坐标

        Returns:
            Optional[str]: 保存的元素图片路径，失败返回None
        """
        img = cv2.imread(source_path)
        if img is None:
            logger.error(f"❌ 无法读取图片: {source_path}")
            return None

        # 边界检查
        height, width = img.shape[:2]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(width, x2)
        y2 = min(height, y2)

        if x2 <= x1 or y2 <= y1:
            logger.error(f"❌ 无效的裁切区域: ({x1},{y1},{x2},{y2})")
            return None

        # 裁切
        cropped = img[y1:y2, x1:x2]

        # 保存
        output_path = os.path.join(self.EXPLORER_ELEMENTS_DIR, f"{element_name}.png")
        cv2.imwrite(output_path, cropped)
        logger.info(f"✂️ 元素已截取: {output_path}")
        return output_path

    # 点击窗口内指定坐标，支持偏移量
    def tap(self, x: int, y: int, dx: int = 0, dy: int = 0) -> bool:
        """
        点击坐标区域

        Args:
            x: 窗口内X坐标
            y: 窗口内Y坐标
            dx: X坐标偏移量
            dy: Y坐标偏移量

        Returns:
            bool: 操作是否成功
        """
        target_x = x + dx
        target_y = y + dy
        screen_coords = self._to_screen_coords(target_x, target_y)
        if not screen_coords:
            return False

        try:
            pyautogui.click(screen_coords[0], screen_coords[1])
            logger.info(f"👆 点击坐标 ({target_x}, {target_y})")
            self.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"❌ 点击失败: {e}")
            return False

    # 输入文本，支持中文（通过剪贴板）
    def input_text(self, text: str) -> bool:
        """
        输入文本

        Args:
            text: 要输入的字符

        Returns:
            bool: 操作是否成功
        """
        try:
            if any(ord(c) > 127 for c in text):
                import pyperclip
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
                logger.info(f"⌨️ 输入文本(剪贴板): {text}")
            else:
                pyautogui.write(text, interval=0.05)
                logger.info(f"⌨️ 输入文本: {text}")
            self.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"❌ 输入失败: {e}")
            return False

    # 使用OCR识别屏幕文字，返回文字中心坐标
    def find_text_by_ocr(self, text: str, timeout: int = 10,
                         region=Normal.ALL,
                         case_sensitive: bool = False) -> Optional[Tuple[int, int]]:
        """
        使用OCR找文字，返回文字坐标

        Args:
            text: 要查找的文字
            timeout: 超时时间（秒）
            region: 识别区域 (x, y, w, h) - 保留用于向后兼容
            region: 搜索区域 (x, y, w, h) 坐标元组
            case_sensitive: 是否区分大小写

        Returns:
            Optional[Tuple[int, int]]: 文字中心坐标，未找到返回None

        示例:
            from utils.aw.region import HALF_UP, HALF_DOWN

            # 在下半部分搜索
            find_text_by_ocr("确认", region=HALF_DOWN)

            # 使用自定义坐标
            find_text_by_ocr("消息", region=(0, 100, 540, 760))
        """
        ocr = self._get_ocr_engine()
        end_time = time.time() + timeout

        while time.time() < end_time:
            img = self.take_screenshot()
            if img is None:
                self.sleep(0.5)
                continue

            dx, dy = 0, 0
            if region:
                x, y, w, h = region
                img = img[y:y + h, x:x + w]
                dx, dy = x, y

            try:
                results = ocr.ocr(img, cls=True)
                if results and results[0]:
                    # 打印页面中识别到的所有文字
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
                            return (center_x, center_y)
            except Exception as e:
                logger.error(f"❌ OCR识别失败: {e}")
                assert False
        logger.warning(f"⚠️ 未找到文字 '{text}'")
        return None

    # 使用模板匹配查找图片，返回图片中心坐标
    def find_image(self, template_name: str, threshold: float = 0.8,
                   timeout: int = 10,
                   region=Normal.ALL) -> Optional[Tuple[int, int]]:
        """
        找图片，返回图片坐标

        Args:
            template_name: 模板图片名称
            threshold: 匹配阈值 (0-1)
            timeout: 超时时间（秒）
            region: 搜索区域 (x, y, w, h) - 保留用于向后兼容
            region: 搜索区域 (x, y, w, h) 坐标元组

        Returns:
            Optional[Tuple[int, int]]: 图片中心坐标，未找到返回None

        示例:
            from utils.aw.region import HALF_UP, HALF_DOWN

            # 在上半部分搜索
            find_image("button.png", region=HALF_UP)

            # 使用自定义坐标
            find_image("icon.png", region=(0, 0, 540, 60))
        """
        # 如果传入的是完整路径（绝对路径），直接使用；否则拼接TEMPLATE_DIR
        if os.path.isabs(template_name):
            template_path = template_name
        else:
            template_path = os.path.join(self.TEMPLATE_DIR, template_name)

        if not os.path.exists(template_path):
            logger.error(f"❌ 模板图片不存在: {template_path}")
            assert None

        # 使用numpy读取文件以支持中文路径
        template = cv2.imdecode(np.fromfile(template_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if template is None:
            logger.error(f"❌ 无法读取模板图片: {template_path}")
            assert None

        template_h, template_w = template.shape[:2]
        end_time = time.time() + timeout

        # 优先使用 region，如果未指定则使用 region (向后兼容)
        actual_region = region if region else region

        while time.time() < end_time:
            img = self.take_screenshot()
            if img is None:
                self.sleep(0.5)
                continue

            dx, dy = 0, 0
            if actual_region:
                x, y, w, h = actual_region
                img = img[y:y + h, x:x + w]
                dx, dy = x, y

            try:
                result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_val >= threshold:
                    center_x = max_loc[0] + template_w // 2 + dx
                    center_y = max_loc[1] + template_h // 2 + dy
                    logger.info(f"🖼️ 找到图片 '{template_name}' @ ({center_x}, {center_y})")
                    return (center_x, center_y)
            except Exception as e:
                logger.error(f"❌ 图片匹配失败: {e}")
                assert False

            self.sleep(0.5)

        # 找不到图片时，截屏保存以便调试
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        template_basename = os.path.basename(template_name).split('.')[0]
        screenshot_name = f"failed_find_{template_basename}_{timestamp}.png"
        screenshot_path = os.path.join(self.SCREENSHOT_DIR, screenshot_name)
        self.take_screenshot(save_path=screenshot_path)
        logger.warning(f"⚠️ 未找到图片 '{template_name}'，已保存截图: {screenshot_path}")
        assert False

    # 使用OCR找到文字后点击
    def click_text(self, text: str, timeout: int = 10,
                   dx: int = 0, dy: int = 0,
                   region=Normal.ALL) -> bool:
        """
        点击文字

        Args:
            text: 要查找并点击的文字
            timeout: 超时时间（秒）
            dx: X坐标偏移量
            dy: Y坐标偏移量
            region: 搜索区域 (x, y, w, h) 坐标元组

        Returns:
            bool: 操作是否成功

        示例:
            from utils.aw.region import HALF_UP, HALF_DOWN

            # 在下半部分查找并点击
            click_text("确认", region=HALF_DOWN)

            # 使用自定义坐标
            click_text("取消", region=(135, 240, 270, 480))
        """
        pos = self.find_text_by_ocr(text, timeout=timeout, region=region)
        if pos:
            return self.tap(pos[0], pos[1], dx, dy)
        return False

    # 使用图像匹配找到图片后点击
    def click_image(self, image: str, threshold: float = 0.8,
                    timeout: int = 10, dx: int = 0, dy: int = 0,
                    region=Normal.ALL):
        """
        点击图片

        Args:
            image: 模板图片名称
            threshold: 匹配阈值 (0-1)
            timeout: 超时时间（秒）
            dx: X坐标偏移量
            dy: Y坐标偏移量
            region: 搜索区域 (x, y, w, h) 坐标元组

        Returns:
            bool: 操作是否成功

        示例:
            from utils.aw.region import HALF_UP, HALF_DOWN

            # 在上半部分查找并点击
            click_image("button.png", region=HALF_UP)

            # 使用自定义坐标
            click_image("icon.png", region=(0, 0, 540, 60))
        """
        pos = self.find_image(image, threshold=threshold, timeout=timeout, region=region)
        if pos:
            return self.tap(pos[0], pos[1], dx, dy)
        assert False, "点击图片失败"

    # 清空输入框（全选后删除）
    def clear_input(self) -> bool:
        """清空输入框"""
        try:
            pyautogui.hotkey('ctrl', 'a')
            self.sleep(0.1)
            pyautogui.press('delete')
            logger.info(f"🗑️ 清空输入框")
            return True
        except Exception as e:
            logger.error(f"❌ 清空失败: {e}")
            return False

    # 按下指定按键（如enter, escape, tab等）
    def press_key(self, key: str) -> bool:
        """按下按键"""
        try:
            pyautogui.press(key)
            logger.info(f"🔘 按键: {key}")
            self.sleep(0.2)
            return True
        except Exception as e:
            logger.error(f"❌ 按键失败: {e}")
            return False

    # 按下返回键（Android的Back键）
    def press_back(self) -> bool:
        """按下返回键"""
        try:
            pyautogui.press('escape')  # 模拟器中escape通常映射为返回
            logger.info(f"🔙 按返回键")
            self.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"❌ 返回键失败: {e}")
            return False

    # 按下Home键
    def press_home(self) -> bool:
        """按下Home键"""
        try:
            # 在模拟器中，通常没有直接的Home键映射，使用ADB命令
            # 这里暂时使用pyautogui的方式
            logger.info(f"🏠 按Home键")
            self.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"❌ Home键失败: {e}")
            return False

    # 从起点滑动到终点
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration: float = 0.3) -> bool:
        """滑动操作"""
        start_coords = self._to_screen_coords(start_x, start_y)
        end_coords = self._to_screen_coords(end_x, end_y)
        if not start_coords or not end_coords:
            return False

        try:
            pyautogui.moveTo(start_coords[0], start_coords[1])
            pyautogui.mouseDown()
            pyautogui.moveTo(end_coords[0], end_coords[1], duration=duration)
            pyautogui.mouseUp()
            logger.info(f"👆 滑动 ({start_x}, {start_y}) -> ({end_x}, {end_y})")
            self.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"❌ 滑动失败: {e}")
            return False

    # 向上滑动（查看更多内容）
    def swipe_up(self, distance: int = 400) -> bool:
        """向上滑动（查看更多内容）"""
        center_x = 270
        start_y = 700
        end_y = start_y - distance
        return self.swipe(center_x, start_y, center_x, end_y, duration=0.3)

    # 向下滑动（返回顶部内容）
    def swipe_down(self, distance: int = 400) -> bool:
        """向下滑动"""
        center_x = 270
        start_y = 300
        end_y = start_y + distance
        return self.swipe(center_x, start_y, center_x, end_y, duration=0.3)

    # 向左滑动
    def swipe_left(self, distance: int = 300) -> bool:
        """向左滑动"""
        center_y = 500
        start_x = 400
        end_x = start_x - distance
        return self.swipe(start_x, center_y, end_x, center_y, duration=0.3)

    # 向右滑动
    def swipe_right(self, distance: int = 300) -> bool:
        """向右滑动"""
        center_y = 500
        start_x = 100
        end_x = start_x + distance
        return self.swipe(start_x, center_y, end_x, center_y, duration=0.3)

    # 等待指定时间（秒）
    def sleep(self, seconds: float) -> None:
        """等待指定时间"""
        time.sleep(seconds)

    # 检查指定文字是否存在于屏幕中
    def text_exists(self, text: str, timeout: int = 5,
                    region=Normal.ALL) -> bool:
        """
        检查文字是否存在

        Args:
            text: 要查找的文字
            timeout: 超时时间（秒）
            region: 搜索区域

        Returns:
            bool: 文字是否存在
        """
        return self.find_text_by_ocr(text, timeout=timeout, region=region) is not None

    # 检查指定图片是否存在于屏幕中
    def image_exists(self, template_name: str, threshold: float = 0.8,
                     timeout: int = 5,
                     region=Normal.ALL) -> bool:
        """
        检查图片是否存在

        Args:
            template_name: 模板图片名称
            threshold: 匹配阈值 (0-1)
            timeout: 超时时间（秒）
            region: 搜索区域

        Returns:
            bool: 图片是否存在
        """
        return self.find_image(template_name, threshold=threshold, timeout=timeout,
                               region=region) is not None

    # 探索当前页面，截图并返回页面信息
    def explore_page(self, page_name: str) -> dict:
        """
        探索当前页面，截图并记录基本信息

        Args:
            page_name: 页面名称

        Returns:
            dict: 页面信息，包含截图路径等
        """
        logger.info(f"📱 开始探索页面: {page_name}")

        # 截取页面
        screenshot_path = self.screenshot_for_explore(f"{page_name}.png")

        # 返回页面信息
        page_info = {
            "name": page_name,
            "screenshot": screenshot_path,
            "timestamp": datetime.now().isoformat(),
            "elements": []
        }

        logger.info(f"✅ 页面探索完成: {page_name}")
        return page_info

    # 执行一系列操作步骤并截图，用于探索操作流程
    def explore_flow(self, flow_name: str, steps: list) -> list:
        """
        探索操作流程，执行一系列操作并截图

        Args:
            flow_name: 流程名称
            steps: 操作步骤列表，每个步骤是一个dict:
                   {"action": "tap", "x": 270, "y": 500, "desc": "点击确定"}
                   {"action": "swipe_up", "desc": "向上滑动"}
                   {"action": "screenshot", "name": "步骤1.png", "desc": "截取结果"}
                   {"action": "wait", "time": 1, "desc": "等待1秒"}

        Returns:
            list: 每个步骤的执行结果
        """
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
