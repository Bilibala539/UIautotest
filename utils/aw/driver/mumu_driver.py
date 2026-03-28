"""
MuMu (Android) 平台驱动

操作目标: MuMu 模拟器设备窗口
底层机制: win32gui (WindowManager) 定位窗口 + pyautogui 截图/点击 + ADB 输入文字
"""
import logging
import subprocess
import time
from typing import Optional, Tuple

import cv2
import numpy as np
import pyautogui

from utils.aw.driver.base_driver import BasePlatformDriver
from utils.window_manager import WindowManager, WindowRect, get_mumu_window_rect

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

logger = logging.getLogger(__name__)


class MuMuDriver(BasePlatformDriver):
    """
    MuMu 模拟器平台驱动

    通过 instance_id 定位 MuMu 设备窗口，使用 pyautogui 截图和鼠标操作。

    Args:
        instance_id: MuMu 模拟器实例 ID (0, 1, 2...)
    """

    def __init__(self, instance_id: int):
        self.instance_id = instance_id
        self._window_rect: Optional[WindowRect] = None

        # 初始化 ADB 连接信息（用于文字输入）
        from utils.devices import get_device_port_by_instance, ADB_PATH
        self._adb_path = ADB_PATH
        self._device_port = get_device_port_by_instance(instance_id)
        self._device_serial = f"127.0.0.1:{self._device_port}"

        logger.info(f"🤖 MuMuDriver 初始化: 实例ID={instance_id}, ADB={self._device_serial}")

    @property
    def platform_name(self) -> str:
        return "mumu"

    # ==================== 窗口操作 ====================

    def get_window_rect(self, refresh: bool = False) -> Optional[Tuple[int, int, int, int]]:
        if refresh or self._window_rect is None:
            self._window_rect = get_mumu_window_rect(self.instance_id)
        if self._window_rect:
            r = self._window_rect
            return (r.left, r.top, r.width, r.height)
        return None

    def to_screen_coords(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        if self._window_rect is None:
            self.get_window_rect()
        if self._window_rect:
            return self._window_rect.to_absolute(x, y)
        logger.error(f"❌ 无法获取窗口区域，实例ID: {self.instance_id}")
        return None

    def focus_window(self) -> bool:
        return WindowManager.focus_window(self.instance_id)

    # ==================== 截图 ====================

    def take_screenshot(self) -> Optional[np.ndarray]:
        rect = self.get_window_rect(refresh=True)
        if not rect:
            logger.error("❌ 无法获取窗口区域进行截图")
            return None

        left, top, width, height = rect
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return img

    # ==================== 点击 ====================

    def tap(self, screen_x: int, screen_y: int) -> bool:
        pyautogui.click(screen_x, screen_y)
        return True

    # ==================== ADB 工具 ====================

    def _adb(self, *args) -> subprocess.CompletedProcess:
        """执行 ADB 命令"""
        cmd = [self._adb_path, "-s", self._device_serial] + list(args)
        try:
            return subprocess.run(cmd, capture_output=True, timeout=15)
        except subprocess.TimeoutExpired:
            logger.error(f"❌ ADB命令超时: {' '.join(cmd)}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ ADB命令失败: {e.stderr.decode()}")
            raise

    # ==================== 输入 ====================

    def input_text(self, text: str) -> bool:
        """
        MuMu 端输入文字 (通过 ADB)

        使用 ADB broadcast 设置 Android 剪贴板 → ADB keyevent 粘贴。
        完全绕过 Windows 输入法问题，直接在 Android 层面操作。

        原理:
        1. adb shell am broadcast 把文字写入 Android 系统剪贴板
        2. adb shell input keyevent 279 (KEYCODE_PASTE) 执行粘贴
        如果 KEYCODE_PASTE 不生效，回退到 Ctrl+V 组合键
        """
        text_str = str(text)

        # 方案: 通过 ADB input text 输入纯 ASCII，
        #       通过 ADB 剪贴板 + 粘贴输入包含非ASCII的文字
        if all(ord(c) < 128 and c not in ' \t\n\r' for c in text_str):
            # 纯 ASCII 且无空格: adb shell input text 最可靠
            self._adb("shell", "input", "text", text_str)
            logger.info(f"⌨️ 输入文本(ADB input): {text_str}")
        else:
            # 含中文/空格等: 通过 ADB 设置剪贴板 → 粘贴
            # 使用 am broadcast 设置剪贴板内容
            self._adb(
                "shell", "am", "broadcast",
                "-a", "clipper.set",
                "-e", "text", text_str
            )
            time.sleep(0.2)
            # KEYCODE_PASTE (279) 粘贴
            self._adb("shell", "input", "keyevent", "279")
            logger.info(f"⌨️ 输入文本(ADB剪贴板): {text_str}")

        return True

    def clear_input(self) -> bool:
        """清空输入框: Ctrl+A 全选 → Delete 删除"""
        # ADB keyevent: KEYCODE_MOVE_HOME=122, KEYCODE_MOVE_END=123 with SHIFT
        # 更简单的方式: 用 pyautogui 发 Ctrl+A + Delete (MuMu 支持这些基础热键)
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
