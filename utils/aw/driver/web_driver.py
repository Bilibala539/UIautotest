"""Selenium 浏览器驱动，供 AWBase 的 OCR 与图像操作复用。"""
from __future__ import annotations

import base64
import logging
from typing import Optional, Tuple

import cv2
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.keys import Keys

from utils.aw.driver.base_driver import BasePlatformDriver

logger = logging.getLogger(__name__)


class SeleniumWebDriver(BasePlatformDriver):
    """将 Selenium WebDriver 适配为 AWBase 所需的平台驱动接口。"""

    def __init__(self, browser):
        self.browser = browser

    @property
    def platform_name(self) -> str:
        return "web"

    def get_window_rect(self, refresh: bool = False) -> Optional[Tuple[int, int, int, int]]:
        size = self.browser.get_window_size()
        return (0, 0, int(size["width"]), int(size["height"]))

    def to_screen_coords(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        return (x, y)

    def focus_window(self) -> bool:
        self.browser.execute_script("window.focus();")
        return True

    def take_screenshot(self) -> Optional[np.ndarray]:
        try:
            raw_png = base64.b64decode(self.browser.get_screenshot_as_base64())
            image = cv2.imdecode(np.frombuffer(raw_png, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                logger.error("❌ 无法解码浏览器截图")
            return image
        except Exception as error:
            logger.error(f"❌ 浏览器截图失败: {error}")
            return None

    def tap(self, screen_x: int, screen_y: int) -> bool:
        try:
            actions = ActionBuilder(self.browser)
            actions.pointer_action.move_to_location(screen_x, screen_y)
            actions.pointer_action.click()
            actions.perform()
            return True
        except Exception as error:
            logger.error(f"❌ 浏览器点击失败 ({screen_x}, {screen_y}): {error}")
            return False

    def long_press(self, screen_x: int, screen_y: int, duration: float = 1.0) -> bool:
        try:
            actions = ActionBuilder(self.browser)
            actions.pointer_action.move_to_location(screen_x, screen_y)
            actions.pointer_action.pointer_down()
            actions.pointer_action.pause(duration)
            actions.pointer_action.pointer_up()
            actions.perform()
            return True
        except Exception as error:
            logger.error(f"❌ 浏览器长按失败 ({screen_x}, {screen_y}): {error}")
            return False

    def input_text(self, text: str) -> bool:
        try:
            ActionChains(self.browser).send_keys(str(text)).perform()
            return True
        except Exception as error:
            logger.error(f"❌ 浏览器输入失败: {error}")
            return False

    def clear_input(self) -> bool:
        try:
            ActionChains(self.browser).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.DELETE).perform()
            return True
        except Exception as error:
            logger.error(f"❌ 浏览器清空输入框失败: {error}")
            return False

    def press_key(self, key: str) -> bool:
        selenium_key = getattr(Keys, key.upper(), key)
        try:
            ActionChains(self.browser).send_keys(selenium_key).perform()
            return True
        except Exception as error:
            logger.error(f"❌ 浏览器按键失败 ({key}): {error}")
            return False

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration: float = 0.3) -> bool:
        try:
            actions = ActionBuilder(self.browser, duration=max(1, int(duration * 1000)))
            actions.pointer_action.move_to_location(start_x, start_y)
            actions.pointer_action.pointer_down()
            actions.pointer_action.move_to_location(end_x, end_y)
            actions.pointer_action.pointer_up()
            actions.perform()
            return True
        except Exception as error:
            logger.error(f"❌ 浏览器拖动失败: {error}")
            return False

    def scroll(self, screen_x: int, screen_y: int, clicks: int) -> bool:
        try:
            self.browser.execute_script("window.scrollBy(0, arguments[0]);", -clicks * 120)
            return True
        except Exception as error:
            logger.error(f"❌ 浏览器滚动失败: {error}")
            return False
