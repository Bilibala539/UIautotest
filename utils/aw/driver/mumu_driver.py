"""
MuMu (Android) 平台驱动

操作目标: MuMu 模拟器设备窗口
底层机制: win32gui (WindowManager) 定位窗口 + pyautogui 截图/点击 + ADB 输入文字

当桌面不可用（屏幕锁定/远程会话断开）时，自动切换到 ADB 模式：
  截图 → adb shell screencap
  点击 → adb shell input tap
  长按 → adb shell input swipe (同点)
  按键 → adb shell input keyevent
  滑动 → adb shell input swipe
"""
import logging
import os
import subprocess
import tempfile
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

# pyautogui key → ADB KEYCODE 映射
_KEY_TO_KEYCODE = {
    "escape": "4",       # KEYCODE_BACK
    "backspace": "67",   # KEYCODE_DEL
    "delete": "112",     # KEYCODE_FORWARD_DEL
    "enter": "66",       # KEYCODE_ENTER
    "return": "66",
    "tab": "61",         # KEYCODE_TAB
    "home": "3",         # KEYCODE_HOME
    "space": "62",       # KEYCODE_SPACE
    "up": "19",
    "down": "20",
    "left": "21",
    "right": "22",
    "sysrq": "120",      # KEYCODE_SYSRQ (系统截图)
}


class MuMuDriver(BasePlatformDriver):
    """
    MuMu 模拟器平台驱动

    通过 instance_id 定位 MuMu 设备窗口，使用 pyautogui 截图和鼠标操作。
    当桌面不可用时自动降级到 ADB 模式。

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

        # 检测桌面是否可用，决定运行模式
        # 默认使用 ADB 模式：更稳定（pyautogui 模式下窗口大小可能与设备分辨率不一致）
        # 设置 FORCE_PYAUTOGUI_MODE=1 可强制使用 pyautogui 模式
        if os.environ.get("FORCE_PYAUTOGUI_MODE") == "1":
            self._adb_mode = not self._check_desktop_available()
        else:
            self._adb_mode = True
        mode_label = "ADB" if self._adb_mode else "pyautogui"
        logger.info(f"🤖 MuMu实例 初始化: 实例ID={instance_id}, ADB={self._device_serial}, 模式={mode_label}")

    @staticmethod
    def _check_desktop_available() -> bool:
        """检测桌面是否可用（能否截图）"""
        # 临时禁用 failsafe 来完成检测
        original_failsafe = pyautogui.FAILSAFE
        pyautogui.FAILSAFE = False
        try:
            pyautogui.screenshot(region=(0, 0, 1, 1))
            # 检查鼠标是否在屏幕角落（会导致后续 failsafe 触发）
            pos = pyautogui.position()
            screen_w, screen_h = pyautogui.size()
            in_corner = pos in [(0, 0), (screen_w - 1, 0), (0, screen_h - 1), (screen_w - 1, screen_h - 1)]
            if in_corner:
                logger.warning("⚠️ 鼠标在屏幕角落，使用 ADB 模式避免 failsafe")
                return False
            return True
        except OSError:
            logger.warning("⚠️ 桌面不可用（屏幕锁定/远程断开），切换到 ADB 模式")
            return False
        finally:
            pyautogui.FAILSAFE = original_failsafe

    @property
    def platform_name(self) -> str:
        return "mumu"

    @property
    def threshold_offset(self) -> float:
        """ADB 截图与 pyautogui 截图存在细微色差，降低匹配阈值补偿"""
        return -0.05 if self._adb_mode else 0.0

    # ==================== 窗口操作 ====================

    def get_window_rect(self, refresh: bool = False) -> Optional[Tuple[int, int, int, int]]:
        if self._adb_mode:
            # ADB 模式：设备屏幕固定 540×960
            return (0, 0, 540, 960)
        if refresh or self._window_rect is None:
            self._window_rect = get_mumu_window_rect(self.instance_id)
        if self._window_rect:
            r = self._window_rect
            return (r.left, r.top, r.width, r.height)
        return None

    def to_screen_coords(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        if self._adb_mode:
            # ADB 模式：坐标已在设备空间，不需要转换
            return (x, y)
        """
        将标准 540x960 坐标映射到实际屏幕坐标

        截图已统一 resize 到 540x960，所以内部操作坐标都是 540x960 空间。
        但实际窗口像素可能因 DPI 缩放而更大（如 125% 下为 675x1200），
        需要按比例映射后再加上窗口偏移。
        """
        rect = self.get_window_rect(refresh=True)
        if not rect:
            logger.error(f"❌ 无法获取窗口区域，实例ID: {self.instance_id}")
            return None

        left, top, width, height = rect
        # 按比例映射: 540x960 → 实际窗口大小
        scale_x = width / self.STANDARD_WIDTH
        scale_y = height / self.STANDARD_HEIGHT
        screen_x = left + int(x * scale_x)
        screen_y = top + int(y * scale_y)
        return (screen_x, screen_y)

    def focus_window(self) -> bool:
        if self._adb_mode:
            return True  # ADB 模式不需要聚焦窗口
        return WindowManager.focus_window(self.instance_id)

    # ==================== 截图 ====================

    # 标准分辨率（所有模板图片和搜索区域都基于此分辨率）
    STANDARD_WIDTH = 540
    STANDARD_HEIGHT = 960

    def take_screenshot(self) -> Optional[np.ndarray]:
        if self._adb_mode:
            return self._take_screenshot_adb()

        rect = self.get_window_rect(refresh=True)
        if not rect:
            logger.error("❌ 无法获取窗口区域进行截图")
            return None

        left, top, width, height = rect
        try:
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
        except OSError:
            logger.warning("⚠️ pyautogui 截图失败，降级到 ADB 截图")
            self._adb_mode = True
            return self._take_screenshot_adb()
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # DPI 缩放适配：如果截图尺寸不是标准 540x960，则 resize 到标准尺寸
        # 确保模板匹配和搜索区域坐标一致
        h, w = img.shape[:2]
        if w != self.STANDARD_WIDTH or h != self.STANDARD_HEIGHT:
            img = cv2.resize(img, (self.STANDARD_WIDTH, self.STANDARD_HEIGHT),
                             interpolation=cv2.INTER_AREA)
        return img

    def _take_screenshot_adb(self) -> Optional[np.ndarray]:
        """通过 ADB screencap 截图"""
        remote_path = "/sdcard/_aw_screenshot.png"
        local_path = os.path.join(tempfile.gettempdir(), f"mumu_screenshot_{self.instance_id}.png")
        try:
            self._adb("shell", "screencap", "-p", remote_path)
            self._adb("pull", remote_path, local_path)
            img = cv2.imdecode(np.fromfile(local_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.error(f"❌ ADB 截图失败: {e}")
            return None

    # ==================== 点击 ====================

    def tap(self, screen_x: int, screen_y: int) -> bool:
        if self._adb_mode:
            self._adb("shell", "input", "tap", str(screen_x), str(screen_y))
            return True
        pyautogui.click(screen_x, screen_y)
        return True

    def long_press(self, screen_x: int, screen_y: int, duration: float = 1.0) -> bool:
        """长按屏幕坐标"""
        if self._adb_mode:
            duration_ms = int(duration * 1000)
            self._adb("shell", "input", "swipe",
                       str(screen_x), str(screen_y),
                       str(screen_x), str(screen_y),
                       str(duration_ms))
            logger.info(f"👆 长按(ADB) ({screen_x}, {screen_y}), 时长={duration}s")
            return True
        pyautogui.moveTo(screen_x, screen_y)
        pyautogui.mouseDown()
        time.sleep(duration)
        pyautogui.mouseUp()
        logger.info(f"👆 长按 ({screen_x}, {screen_y}), 时长={duration}s")
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

        使用 adb shell input text 输入纯 ASCII 文字。
        """
        text_str = str(text)
        self._adb("shell", "input", "text", text_str)
        logger.info(f"⌨️ 输入文本(ADB input): {text_str}")
        return True

    def clear_input(self) -> bool:
        """清空输入框: Ctrl+A 全选 → Delete 删除"""
        if self._adb_mode:
            # ADB 模式: 使用 keycombination 发送 Ctrl+A，再发 DEL
            self._adb("shell", "input", "keycombination", "113", "29")  # CTRL_LEFT + A
            time.sleep(0.1)
            self._adb("shell", "input", "keyevent", "112")  # FORWARD_DEL
            logger.info("🗑️ 清空输入框(ADB)")
            return True
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        logger.info("🗑️ 清空输入框")
        return True

    # ==================== 按键 ====================

    def press_key(self, key: str) -> bool:
        if self._adb_mode:
            keycode = _KEY_TO_KEYCODE.get(key.lower())
            if keycode:
                self._adb("shell", "input", "keyevent", keycode)
                logger.info(f"🔘 按键(ADB): {key} → keycode {keycode}")
            else:
                logger.warning(f"⚠️ 未知按键: {key}, 尝试 pyautogui")
                pyautogui.press(key)
            return True
        pyautogui.press(key)
        logger.info(f"🔘 按键: {key}")
        return True

    # ==================== 滑动 / 滚动 ====================

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration: float = 0.3) -> bool:
        if self._adb_mode:
            duration_ms = int(duration * 1000)
            self._adb("shell", "input", "swipe",
                       str(start_x), str(start_y),
                       str(end_x), str(end_y),
                       str(duration_ms))
            logger.info(f"👆 滑动(ADB) ({start_x},{start_y}) → ({end_x},{end_y})")
            return True
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(end_x, end_y, duration=duration)
        pyautogui.mouseUp()
        logger.info(f"👆 滑动 ({start_x},{start_y}) → ({end_x},{end_y})")
        return True

    def scroll(self, screen_x: int, screen_y: int, clicks: int) -> bool:
        if self._adb_mode:
            # ADB 模拟滚动: 正数向上滑，负数向下滑
            distance = clicks * 100
            self._adb("shell", "input", "swipe",
                       str(screen_x), str(screen_y),
                       str(screen_x), str(screen_y - distance),
                       "300")
            logger.info(f"🖱️ 滚动(ADB) @ ({screen_x},{screen_y}), clicks={clicks}")
            return True
        pyautogui.scroll(clicks, x=screen_x, y=screen_y)
        logger.info(f"🖱️ 滚动 @ ({screen_x},{screen_y}), clicks={clicks}")
        return True
