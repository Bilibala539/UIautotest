"""通过系统 ADB 连接安卓实机的基础平台驱动。"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import re
import xml.etree.ElementTree as ElementTree
from typing import Optional, Tuple

import cv2
import numpy as np

from utils.aw.driver.base_driver import BasePlatformDriver

logger = logging.getLogger(__name__)

_KEYCODES = {
    "escape": "KEYCODE_BACK",
    "back": "KEYCODE_BACK",
    "backspace": "KEYCODE_DEL",
    "delete": "KEYCODE_FORWARD_DEL",
    "enter": "KEYCODE_ENTER",
    "return": "KEYCODE_ENTER",
    "tab": "KEYCODE_TAB",
    "home": "KEYCODE_HOME",
    "space": "KEYCODE_SPACE",
    "up": "KEYCODE_DPAD_UP",
    "down": "KEYCODE_DPAD_DOWN",
    "left": "KEYCODE_DPAD_LEFT",
    "right": "KEYCODE_DPAD_RIGHT",
}


class AndroidAdbDriver(BasePlatformDriver):
    """ADB 驱动，支持 USB 或网络连接的安卓真实设备。

    ``ANDROID_DEVICE_SERIAL`` 指定 ``adb devices`` 中的 serial；如果未指定，
    仅当 ADB 只发现一台设备时自动使用该设备。ADB 可执行文件默认从 PATH 查找，
    也可通过 ``ADB_PATH`` 指定。
    """

    def __init__(self, serial: Optional[str] = None, adb_path: Optional[str] = None):
        self.serial = (serial or os.environ.get("ANDROID_DEVICE_SERIAL")
                       or os.environ.get("ANDROID_SERIAL", "")).strip()
        self.adb_path = adb_path or os.environ.get("ADB_PATH") or shutil.which("adb")
        if not self.adb_path:
            raise FileNotFoundError("找不到 adb，请安装 Android SDK Platform-Tools 并设置 ADB_PATH")
        self._window_size: Optional[Tuple[int, int]] = None
        self._ensure_device_selected()

    @property
    def platform_name(self) -> str:
        return "android"

    def _base_command(self) -> list[str]:
        command = [self.adb_path]
        if self.serial:
            command.extend(["-s", self.serial])
        return command

    def _run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        result = subprocess.run(
            [*self._base_command(), *args],
            capture_output=True,
            timeout=30,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if check and result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"ADB 命令失败: {' '.join(args)}; {stderr}")
        return result

    def _ensure_device_selected(self) -> None:
        if self.serial:
            result = self._run("get-state", check=False)
            if result.returncode != 0 or result.stdout.decode(errors="replace").strip() != "device":
                raise RuntimeError(f"ADB 设备不可用: {self.serial}")
            return

        result = subprocess.run(
            [self.adb_path, "devices"],
            capture_output=True,
            timeout=30,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode != 0:
            raise RuntimeError("无法执行 adb devices")
        devices = []
        for line in result.stdout.decode("utf-8", errors="replace").splitlines()[1:]:
            fields = line.split()
            if len(fields) >= 2 and fields[1] == "device":
                devices.append(fields[0])
        if len(devices) != 1:
            raise RuntimeError(f"请设置 ANDROID_DEVICE_SERIAL；当前可用设备数: {len(devices)}")
        self.serial = devices[0]

    def get_window_rect(self, refresh: bool = False) -> Optional[Tuple[int, int, int, int]]:
        if refresh or self._window_size is None:
            result = self._run("shell", "wm", "size")
            output = result.stdout.decode("utf-8", errors="replace")
            import re
            match = re.search(r"Physical size:\s*(\d+)x(\d+)", output)
            if not match:
                match = re.search(r"Override size:\s*(\d+)x(\d+)", output)
            if match:
                self._window_size = (int(match.group(1)), int(match.group(2)))
        if self._window_size:
            return (0, 0, self._window_size[0], self._window_size[1])
        return None

    def dump_nodes(self) -> list[dict]:
        """Dump 当前界面 UIAutomator 层级，返回节点信息列表。

        每个节点包含：resource_id / text / content_desc / class_name /
        bounds / center / clickable / scrollable。explorer 探索和
        accessibility key 校验的唯一合法数据源。
        """
        dump_path = "/sdcard/uiat_aw_hierarchy.xml"
        self._run("shell", "uiautomator", "dump", dump_path, check=False)
        result = self._run("shell", "cat", dump_path, check=False)
        if result.returncode != 0:
            logger.warning("uiautomator dump 失败")
            return []
        xml_text = result.stdout.decode("utf-8", errors="replace")
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError:
            logger.warning("uiautomator dump XML 解析失败")
            return []
        nodes = []
        for node in root.iter("node"):
            attrs = node.attrib
            bounds = attrs.get("bounds", "")
            match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
            center: Optional[Tuple[int, int]] = None
            box: Optional[Tuple[int, int, int, int]] = None
            if match:
                left, top, right, bottom = (int(v) for v in match.groups())
                box = (left, top, right, bottom)
                center = ((left + right) // 2, (top + bottom) // 2)
            nodes.append({
                "resource_id": attrs.get("resource-id", ""),
                "text": attrs.get("text", ""),
                "content_desc": attrs.get("content-desc", ""),
                "class_name": attrs.get("class", ""),
                "bounds": box,
                "center": center,
                "clickable": attrs.get("clickable") == "true",
                "scrollable": attrs.get("scrollable") == "true",
            })
        return nodes

    @staticmethod
    def _node_id_matches(node_id: str, resource_id: str) -> bool:
        return bool(node_id) and (
            node_id == resource_id or node_id.endswith(f"/{resource_id}")
        )

    def find_nodes(self, resource_id: str) -> list[dict]:
        """返回 resource_id 匹配的所有语义节点（精确或包名前缀结尾匹配）。"""
        return [n for n in self.dump_nodes()
                if self._node_id_matches(n["resource_id"], resource_id)]

    def accessibility_exists(self, resource_id: str) -> bool:
        """判断 resource_id 对应的语义节点是否存在。"""
        return bool(self.find_nodes(resource_id))

    def find_node_center(self, resource_id: str) -> Optional[Tuple[int, int]]:
        """Return the center of an Android UIAutomator resource-id node."""
        for node in self.find_nodes(resource_id):
            if node["center"] is not None:
                return node["center"]
        return None

    def to_screen_coords(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        return (x, y)

    def focus_window(self) -> bool:
        return True

    def take_screenshot(self) -> Optional[np.ndarray]:
        try:
            result = self._run("exec-out", "screencap", "-p")
            image = cv2.imdecode(np.frombuffer(result.stdout, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                logger.error("❌ 无法解码安卓实机截图")
            return image
        except Exception as error:
            logger.error(f"❌ 安卓实机截图失败: {error}")
            return None

    def tap(self, screen_x: int, screen_y: int) -> bool:
        self._run("shell", "input", "tap", str(screen_x), str(screen_y))
        return True

    def long_press(self, screen_x: int, screen_y: int, duration: float = 1.0) -> bool:
        duration_ms = max(1, int(duration * 1000))
        self._run("shell", "input", "swipe", str(screen_x), str(screen_y),
                  str(screen_x), str(screen_y), str(duration_ms))
        return True

    def input_text(self, text: str) -> bool:
        value = str(text).replace("%", "%25").replace(" ", "%s")
        self._run("shell", "input", "text", value)
        return True

    def clear_input(self) -> bool:
        self._run("shell", "input", "keyevent", "KEYCODE_CTRL_LEFT")
        self._run("shell", "input", "keyevent", "KEYCODE_A")
        self._run("shell", "input", "keyevent", "KEYCODE_DEL")
        return True

    def press_key(self, key: str) -> bool:
        keycode = _KEYCODES.get(key.lower(), key)
        self._run("shell", "input", "keyevent", keycode)
        return True

    def start_app(self, package: str, activity: str | None = None) -> bool:
        """Start an Android application through the standard launcher."""
        if activity:
            component = f"{package}/{activity.lstrip('/')}"
            self._run("shell", "am", "start", "-n", component)
        else:
            self._run("shell", "monkey", "-p", package, "1")
        return True

    def stop_app(self, package: str) -> bool:
        """Stop an Android application without affecting the device session."""
        self._run("shell", "am", "force-stop", package)
        return True

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration: float = 0.3) -> bool:
        duration_ms = max(1, int(duration * 1000))
        self._run("shell", "input", "swipe", str(start_x), str(start_y),
                  str(end_x), str(end_y), str(duration_ms))
        return True

    def scroll(self, screen_x: int, screen_y: int, clicks: int) -> bool:
        distance = clicks * 120
        return self.swipe(screen_x, screen_y, screen_x, screen_y - distance)
