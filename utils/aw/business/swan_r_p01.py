"""Swan 回归批量转换 P01 包级 mixin（M01 启动隐私 + M03 主框架导航）。

本文件为批次新增（tcbatch P01），仅承载本包复用的新业务方法；挂入
SwanBusiness MRO 由集成方统一处理（禁改 utils/aw/business/swan.py）。
定位口径：OCR 文本优先；region 常量为 720x1600 截图口径的 OCR 收窄带
（非坐标定位，同 utils/aw/business/swan.py 既有 region 注记口径）。
"""
from __future__ import annotations

import os
import time

from image.image_name_mapping import (
    SWAN_TAB_DEVICE,
    SWAN_TAB_HOME,
    SWAN_TAB_ME,
    SWAN_TAB_PLATFORM,
)

# 底部迷你播放条 band（720x1600 口径，播放条 y≈1376-1476，同 swan.py
# _DEVICE_OCR_BOTTOM_LIMIT 注）：会话态下播放条内容（曲目/设备名）持续
# 偏离无会话态模板 SWAN_BOTTOM_PLAYER_BAR（verify-run3 口径），band 内
# OCR 非空作为「迷你播放条在屏」的可观察判据；无播放条时该 band 为
# 尾部留白空白区
_MINI_PLAYER_BAR_REGION = (0, 1340, 720, 140)

# 底部导航标签 band（720x1600 口径，导航栏位于播放条带之下 y≈1476-1600）：
# 同页重复点 Tab 用标签文案 [OCR] 定位（选中态图标无未选中态模板），
# region 收窄防页面内容区同名文案误点
_BOTTOM_NAV_LABEL_REGION = (0, 1470, 720, 130)


class SwanRP01Mixin:
    """P01 包级复用方法（M01 隐私弹层链 / M03 导航壳压测）。"""

    def privacy_dialog_visible(self, timeout: float = 2.0) -> bool:
        """隐私弹层可见性探测：弹层标题「用户隐私协议概要」[OCR] 命中。

        文案同 android_base.APP_POPUP_RULES 首启隐私白名单标记；用于
        全新安装/未同意态（privacyRequired 窗口）条件用例的前置探测，
        弹层不存在返回 False 不断言。
        """
        return self.find_text_by_ocr("用户隐私协议概要",
                                     timeout=int(timeout)) is not None

    def accept_privacy_dialog(self) -> None:
        """点击隐私弹层「同意」并断言弹层关闭（privacyRequired→loginRequired）。"""
        self.click_text("同意", timeout=10)
        assert self.find_text_by_ocr("用户隐私协议概要", timeout=3) is None, (
            "点击同意后隐私弹层仍在屏（弹层未关闭或 OCR 残留，请核对现场截图）")

    def force_stop_cold_start(self) -> None:
        """杀进程级冷启动（stop_app → start_app），不做首启弹窗处置。

        与 cold_start_assert 的差异：不调 dismiss_app_popups——隐私必答
        态用例需要弹层跨进程终止原样存活（弹窗处置会误点「同意」烧毁
        未同意态）；落页/弹层断言由调用方按用例语义自行执行。
        """
        package = os.environ.get("SWAN_PACKAGE", "com.swan.network")
        self.driver.stop_app(package)
        self.driver.start_app(package)

    def assert_mini_player_bar_text(self, timeout: int = 6) -> None:
        """断言迷你播放条在屏：播放条 band [OCR] 轮询到非空文本行。

        会话态下播放条内容持续偏离无会话态模板 SWAN_BOTTOM_PLAYER_BAR
        （verify-run3 口径），故以 band 内 OCR 非空为可观察判据。
        仅限壳层/白名单页调用（push 页内容可能入带造成误判）。
        """
        deadline = time.monotonic() + timeout
        while True:
            items = self.ocr_scan_page(region=_MINI_PLAYER_BAR_REGION)
            if any((i.get("text") or "").strip() for i in items):
                return
            if time.monotonic() >= deadline:
                break
            self.sleep(0.5)
        assert False, (
            "迷你播放条不在屏（播放条 band [OCR] 无文本行；播放会话丢失或"
            "该页非白名单路由？）")

    def rapid_tab_cycle(self, cycles: int = 1) -> None:
        """底部四 Tab 连续轮切 cycles 圈（平台→设备→我的→首页，坑 5 压测）。

        用未选中态 Tab 图 [图] 直接连点：该轮转序下目标 Tab 恒为未选中态，
        模板必可命中（若从首页起切，首页选中态图恰不可见会误报失败，故
        固定从平台起切）；不做逐次到位断言（连切节奏优先），终态由调用方
        go_bottom_tab 收口断言。
        """
        for _ in range(cycles):
            for template in (SWAN_TAB_PLATFORM, SWAN_TAB_DEVICE,
                             SWAN_TAB_ME, SWAN_TAB_HOME):
                self.click_image(template, timeout=5)

    def reclick_bottom_tab_label(self, label: str, clicks: int = 3) -> None:
        """同页重复点击当前底部 Tab（导航标签 [OCR] 定位，连点 clicks 次）。

        选中态 Tab 无未选中态模板可点，改按导航栏标签文案 [OCR]；
        region 收窄到底部导航标签带，防设备页内容区同名文案误点。
        """
        for _ in range(clicks):
            self.click_text(label, timeout=5, region=_BOTTOM_NAV_LABEL_REGION)

    def assert_app_exited(self, package: str, timeout: float = 5.0) -> None:
        """断言 App 进程已退出：前台包名轮询至异于 package（exitApp 取证）。

        launch-NEG-006「不同意」真退出取证口径：进程级证据取自 driver
        get_foreground_package()（dumpsys window mCurrentFocus 系统级事实，
        非 UI 面断言）——若 App 仅页面返回而非进程退出，前台包名仍为本
        包名，断言即失败。
        """
        deadline = time.monotonic() + timeout
        while True:
            foreground = self.driver.get_foreground_package()
            if foreground is not None and foreground != package:
                return
            if time.monotonic() >= deadline:
                break
            self.sleep(0.5)
        assert False, (
            f"触发退出后 {timeout}s 内前台包名仍为 {package}"
            "（App 未退出/exitApp 语义被破坏，或前台读取失败——核对证据帧）")
