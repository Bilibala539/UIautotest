"""Android 端基础操作（AndroidBaseAW）。

按键、返回、Home 等 Android 系统级操作收敛在这里。
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from utils.aw.aw_base import AWBase, _screenshot_on_failure

logger = logging.getLogger(__name__)


class AndroidBaseAW(AWBase):
    """android 端基础操作，继承公共引擎 AWBase。"""

    # ==================== 系统按键 ====================

    def press_key(self, key: str, long_press: bool = False) -> bool:
        """按下系统按键（如 'escape'、'home'）；long_press=True 长按（音量键等）。"""
        result = self.driver.press_key(key, long_press=long_press)
        self.sleep(0.2)
        return result

    def press_back(self) -> bool:
        """按返回键。"""
        logger.info("🔙 按返回键")
        return self.press_key('escape')

    def press_home(self) -> bool:
        """按 Home 键。"""
        return self.press_key('home')

    # ==================== 首启弹窗自动处置 ====================

    # (界面标志文字含匹配, 按钮/动作文字精确匹配);新弹窗=追加一条规则
    APP_POPUP_RULES: tuple[tuple[str, str], ...] = (
        ("用户隐私协议概要", "同意"),      # App 首启隐私协议
        ("欢迎使用Swan Audio", "稍后再说"),  # 平台授权弹窗(授权需先勾选置灰,只点稍后再说)
        ("是否允许", "允许"),              # Android 系统权限弹窗
    )

    def dismiss_app_popups(self, rules: tuple[tuple[str, str], ...] = APP_POPUP_RULES,
                           rounds: int = 3) -> list[str]:
        """打开 App 后自动检测并处置首启/系统弹窗(用户拍板的框架级检测)。

        标志文字出现才动作,按钮按文字精确匹配(经语义节点定位,不写坐标);
        白名单外的弹窗不动,只记 WARNING 供人工补规则。返回处置记录。
        """
        handled: list[str] = []
        for _ in range(rounds):
            nodes = self.driver.dump_nodes()
            hit = None
            for marker, button in rules:
                if not any(marker in (n["text"] or "") or marker in (n["content_desc"] or "")
                           for n in nodes):
                    continue
                target = next((n for n in nodes
                               if button in (n["text"], n["content_desc"]) and n["center"]), None)
                if target is None:
                    logger.warning(f"弹窗 '{marker}' 出现但未找到按钮 '{button}',跳过(需补规则)")
                    continue
                hit = (marker, button, target)
                break
            if hit is None:
                return handled
            marker, button, target = hit
            logger.info(f"自动处置弹窗 '{marker}' → 点击 '{button}'")
            self.tap(*target["center"])
            handled.append(marker)
            self.sleep(1.5)  # 关闭动画后可能还有下一层弹窗
        logger.warning(f"弹窗处置 {rounds} 轮未清空,已处置: {handled}(界面可能仍有弹窗)")
        return handled

    # ==================== 系统 WiFi 连接 ====================

    # WiFi 设置页关键节点（HONOR JDY-AN00 / Android 14 com.android.settings 实测）
    WIFI_SSID_TITLE_ID = "android:id/title"                        # 列表页 SSID 文本节点
    WIFI_PASSWORD_ID = "com.android.settings:id/password"          # 密码输入框
    WIFI_CONNECT_BTN_ID = "com.android.settings:id/btn_wifi_connect"  # 密码页"连接"钮
    WIFI_CANCEL_BTN_ID = "com.android.settings:id/btn_wifi_cancel"    # 密码页"取消"钮
    # 无互联网确认弹窗处置规则（标志文字, 按钮文字）——HONOR 实际文案待热点配网实测补齐,
    # 未命中白名单时 dismiss_app_popups 只记 WARNING 不误点
    WIFI_NO_INTERNET_RULES: tuple[tuple[str, str], ...] = (
        ("此网络无法访问互联网", "保持连接"),
        ("无法上网", "仍要连接"),
    )

    def connect_wifi(self, ssid: str, password: Optional[str] = None,
                     timeout: float = 30.0) -> bool:
        """连接指定 WiFi（系统 WLAN 设置页 UI 自动化，用户拍板替代 adb cmd 方案）。

        背景：HONOR 阉割了 adb cmd wifi connect-network（Uid 2000 无权限），
        且 add-suggestion 是 auto-join 语义不保证立即连接；热点配网必须跳出
        App 连系统 WiFi，故走设置页。系统页不在 App 定位策略（图>OCR）约束内，
        用 dump_nodes 语义节点定位（同 dismiss_app_popups 系统弹窗先例），
        不写死坐标；连接结果用 driver.wifi_current_ssid()（cmd wifi status）
        断言，不占 UI 步骤。

        前置：WiFi 已开启（否则超时报错；可先 adb shell cmd wifi set-wifi-enabled
        enabled）。成功后停在系统设置页，回 App 由业务层负责（start_app）。
        已连目标网时幂等直接返回 True。

        Args:
            ssid: 目标网络名（列表页按 SSID 文本精确匹配定位）
            password: 密码；已保存网络/开放网络传 None。仅支持 ASCII
                （走 adb input text，空格已转义）
            timeout: 找 SSID 与确认连接各自的最长等待秒数

        Returns:
            bool: 连接成功

        Raises:
            RuntimeError: 列表中未找到 SSID / 需要密码未提供 / 连接确认超时
        """
        current = self.driver.wifi_current_ssid()
        if current == ssid:
            logger.info(f"✅ WiFi 已连接 '{ssid}'，无需操作")
            return True

        self.driver.start_action("android.settings.WIFI_SETTINGS")
        self.sleep(2.0)  # 设置页加载
        self._scroll_wifi_to_top()  # 页面可能保留上次的滚动位置，先回顶

        row = self._wait_wifi_row(ssid, timeout)
        logger.info(f"👆 点击 WLAN 列表项 '{ssid}'")
        self.tap(*row["center"])

        self._handle_wifi_password_page(password)
        self._verify_wifi_connected(ssid, timeout)
        self._dismiss_no_internet_dialog()
        logger.info(f"✅ WiFi 连接成功: '{ssid}'")
        return True

    def _wait_wifi_row(self, ssid: str, timeout: float) -> dict:
        """轮询等待 WLAN 列表出现目标 SSID 节点（扫描列表自动刷新，含滚动）。

        返回 resource_id=android:id/title 且 text==ssid 的节点；超时抛 RuntimeError。
        """
        deadline = time.monotonic() + timeout
        round_idx = 0
        while time.monotonic() < deadline:
            round_idx += 1
            for node in self.driver.find_nodes_by_text(ssid):
                if node["resource_id"] == self.WIFI_SSID_TITLE_ID and node["center"]:
                    return node
            if round_idx % 2 == 0:
                self._scroll_wifi_list()
            self.sleep(1.5)
        raise RuntimeError(
            f"WiFi 列表中未找到 '{ssid}'（{timeout}s 含滚动）。"
            f"若 WiFi 未开启请先 cmd wifi set-wifi-enabled enabled")

    def _scroll_wifi_list(self) -> None:
        """按设备分辨率自适应向下滑一屏（展示列表更下方条目）。"""
        rect = self.driver.get_window_rect()
        if not rect:
            return
        _, _, w, h = rect
        self.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3))

    def _scroll_wifi_to_top(self, times: int = 2) -> None:
        """向上滚动回列表顶部（起点在列表中部，避免拉出通知栏）。"""
        rect = self.driver.get_window_rect()
        if not rect:
            return
        _, _, w, h = rect
        for _ in range(times):
            self.swipe(w // 2, int(h * 0.25), w // 2, int(h * 0.75))
            self.sleep(0.3)

    def _handle_wifi_password_page(self, password: Optional[str]) -> None:
        """若点选后进入密码页：输密码点连接；未提供密码则取消并报错。"""
        field = next((n for n in self.driver.dump_nodes()
                      if n["resource_id"] == self.WIFI_PASSWORD_ID and n["center"]), None)
        if field is None:
            return  # 开放网络/已保存网络，直接进入连接流程
        if password is None:
            cancel = next((n for n in self.driver.dump_nodes()
                           if n["resource_id"] == self.WIFI_CANCEL_BTN_ID and n["center"]), None)
            if cancel:
                self.tap(*cancel["center"])
            raise RuntimeError("目标 WiFi 需要密码但未提供 password 参数")
        self.tap(*field["center"])  # 聚焦密码框（通常已自动聚焦，兜底）
        self.sleep(0.5)
        self.input_text(password)
        connect = next((n for n in self.driver.dump_nodes()
                        if n["resource_id"] == self.WIFI_CONNECT_BTN_ID and n["center"]), None)
        assert connect is not None, "WiFi 密码页未找到'连接'按钮（页面结构变化？）"
        self.tap(*connect["center"])
        self.sleep(1.0)  # 发起连接

    def _verify_wifi_connected(self, ssid: str, timeout: float) -> None:
        """轮询 cmd wifi status 确认连上目标 SSID，超时抛 RuntimeError。"""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.driver.wifi_current_ssid() == ssid:
                return
            self.sleep(1.5)
        current = self.driver.wifi_current_ssid()
        raise RuntimeError(
            f"连接 WiFi '{ssid}' 确认超时（{timeout}s），当前: {current or '未连接'}")

    def _dismiss_no_internet_dialog(self, rounds: int = 2) -> list[str]:
        """连上无互联网网络（如音箱热点）后系统可能弹确认框，按白名单处置。"""
        return self.dismiss_app_popups(rules=self.WIFI_NO_INTERNET_RULES, rounds=rounds)
