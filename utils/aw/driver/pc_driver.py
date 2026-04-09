"""
PC (Windows) 平台驱动

操作目标: Windows 原生桌面应用窗口（默认: 网易POPO PC客户端）
底层机制: win32gui 定位窗口 + mss 截图（支持多显示器/负坐标）
          + pyautogui 鼠标 + 剪贴板输入 (Ctrl+V，彻底规避 IME 问题)
"""
import ctypes
import logging
import time
from typing import Optional, Tuple, List

import cv2
import numpy as np
import pyautogui
import pyperclip
import mss
import win32gui
import win32con

from utils.aw.driver.base_driver import BasePlatformDriver

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

logger = logging.getLogger(__name__)


class PCDriver(BasePlatformDriver):
    """
    PC (Windows) 平台驱动

    通过窗口标题关键词定位目标窗口，使用 mss 截图（支持多显示器），
    pyautogui 鼠标操作，剪贴板方式输入文字。

    Args:
        window_keywords: 目标窗口标题关键词列表，默认为网易POPO PC客户端
    """

    DEFAULT_WINDOW_KEYWORDS = ["网易POPO", "POPO"]

    def __init__(self, window_keywords: Optional[List[str]] = None):
        self.window_keywords = window_keywords or self.DEFAULT_WINDOW_KEYWORDS
        self._hwnd: Optional[int] = None
        self._window_rect: Optional[Tuple[int, int, int, int]] = None
        logger.info(f"🖥️ PCDriver 初始化: 窗口关键词={self.window_keywords}")

    @property
    def platform_name(self) -> str:
        return "pc"

    # ==================== 内部: 窗口查找 ====================

    def _find_window(self) -> Optional[int]:
        """枚举所有可见窗口，找到匹配关键词的目标窗口 hwnd"""
        found = []

        def _cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                for kw in self.window_keywords:
                    if kw.lower() in title.lower():
                        found.append((hwnd, title))
                        break
            return True

        win32gui.EnumWindows(_cb, None)

        if not found:
            logger.error(f"❌ 未找到窗口 (关键词: {self.window_keywords})")
            return None

        found.sort(key=lambda x: len(x[1]))
        hwnd, title = found[0]
        logger.info(f"✅ 找到目标窗口: [{title}]  hwnd={hwnd}")
        return hwnd

    def _get_hwnd(self, refresh: bool = False) -> Optional[int]:
        """获取目标窗口句柄（带缓存）"""
        if refresh or self._hwnd is None or not win32gui.IsWindow(self._hwnd):
            self._hwnd = self._find_window()
        return self._hwnd

    # ==================== 窗口操作 ====================

    def get_window_rect(self, refresh: bool = False) -> Optional[Tuple[int, int, int, int]]:
        if not refresh and self._window_rect:
            return self._window_rect

        hwnd = self._get_hwnd()
        if not hwnd:
            return None

        try:
            pt = win32gui.ClientToScreen(hwnd, (0, 0))
            cr = win32gui.GetClientRect(hwnd)
            left, top = pt
            width, height = cr[2], cr[3]
            self._window_rect = (left, top, width, height)
            return self._window_rect
        except Exception as e:
            logger.error(f"❌ 获取窗口区域失败: {e}")
            return None

    def to_screen_coords(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        rect = self.get_window_rect()
        if not rect:
            return None
        left, top, _, _ = rect
        return left + x, top + y

    def focus_window(self) -> bool:
        """将目标窗口置于前台（绕过 Windows SetForegroundWindow 限制）"""
        hwnd = self._get_hwnd()
        if not hwnd:
            return False
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            cur_tid = ctypes.windll.kernel32.GetCurrentThreadId()
            tgt_tid = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
            attached = False
            if cur_tid != tgt_tid:
                attached = ctypes.windll.user32.AttachThreadInput(cur_tid, tgt_tid, True)
            try:
                ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
                win32gui.BringWindowToTop(hwnd)
                win32gui.SetForegroundWindow(hwnd)
                ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                )
            finally:
                if attached:
                    ctypes.windll.user32.AttachThreadInput(cur_tid, tgt_tid, False)

            time.sleep(0.3)
            logger.info("✅ 窗口已置于前台")
            return True
        except Exception as e:
            logger.error(f"❌ 置前窗口失败: {e}")
            return False

    # ==================== 截图 ====================

    def take_screenshot(self) -> Optional[np.ndarray]:
        rect = self.get_window_rect(refresh=True)
        if not rect:
            logger.error("❌ 无法获取窗口区域，截图失败")
            return None

        left, top, width, height = rect
        with mss.mss() as sct:
            raw = sct.grab({"left": left, "top": top, "width": width, "height": height})
            img = cv2.cvtColor(np.array(raw), cv2.COLOR_BGRA2BGR)
        return img

    # ==================== 点击 ====================

    def tap(self, screen_x: int, screen_y: int) -> bool:
        pyautogui.click(screen_x, screen_y)
        return True

    def long_press(self, screen_x: int, screen_y: int, duration: float = 1.0) -> bool:
        """长按屏幕坐标"""
        pyautogui.moveTo(screen_x, screen_y)
        pyautogui.mouseDown()
        time.sleep(duration)
        pyautogui.mouseUp()
        logger.info(f"👆 长按 ({screen_x}, {screen_y}), 时长={duration}s")
        return True

    # ==================== 输入 ====================

    def input_text(self, text: str) -> bool:
        """
        PC 端输入文字

        始终使用剪贴板粘贴 (Ctrl+V)，彻底规避输入法 (IME) 问题。
        """
        pyperclip.copy(str(text))
        pyautogui.hotkey('ctrl', 'v')
        logger.info(f"⌨️ 输入文字(剪贴板): {text}")
        return True

    def clear_input(self) -> bool:
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        logger.info("🗑️ 清空输入框")
        return True

    # ==================== 按键 ====================

    def press_key(self, key: str) -> bool:
        pyautogui.press(key)
        logger.info(f"🔘 按键: {key}")
        return True

    # ==================== 滑动 / 滚动 ====================

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration: float = 0.3) -> bool:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(end_x, end_y, duration=duration)
        pyautogui.mouseUp()
        logger.info(f"👆 滑动 ({start_x},{start_y}) → ({end_x},{end_y})")
        return True

    def scroll(self, screen_x: int, screen_y: int, clicks: int) -> bool:
        pyautogui.scroll(clicks, x=screen_x, y=screen_y)
        logger.info(f"🖱️ 滚动 @ ({screen_x},{screen_y}), clicks={clicks}")
        return True
