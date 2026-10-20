# CASE-ID: music-POS-031
"""Swan 回归·M07 Qobuz:奖项弹层·仅信息入口不改导航(music-POS-031)。

步骤→AW 映射(QobuzAwardsBottomSheet,无独立路由,月桂图标入口):
  1. Qobuz 主页点奖项标识入口 → open_platform_home('qobuz') + 入口探测
     (OCR '奖项'/'Accolades' 文本;月桂图标 OCR 不稳,未命中留模板标定提示)
     → 奖项弹层打开(锚 ['奖项','获奖','Accolades'])
  2. 浏览后关闭弹层 → press_back()(底部弹层 back 收束) → 停留 Qobuz 主页
     (导航栈未变化:主页锚「Qobuz」仍在)

cleanup: 无(弹层关闭即还原);框架每用例冷启动。
B 标定说明:月桂图标入口与奖项弹层内容无知识库档案,文本变体探测+失败
留模板标定提示;月桂图标 [图] 模板真机补截后回填
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos031QobuzAwardsSheet(BaseTest):
    """Qobuz 奖项弹层可打开可关闭,导航栈不变。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qobuz_awards_bottom_sheet(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:Qobuz 主页 → 奖项标识入口(文本变体探测,月桂图标待模板)
        self.userA.open_platform_home("qobuz")
        entry = None
        for word in ("奖项", "Accolades"):
            entry = self.userA.find_text_by_ocr(word, timeout=2)
            if entry is not None:
                break
        assert entry is not None, (
            "Qobuz 主页未扫到奖项标识入口(奖项/Accolades 文本均未命中;"
            "月桂图标为图形元素,[图] 模板待补截,"
            "见 package_report.json template_needs)")
        self.userA.tap(entry["cx"], entry["cy"])
        self.userA.assert_any_text(["奖项", "获奖", "Accolades"])
        # 步骤 2:关闭弹层,停留原页面(导航栈未变化)
        self.userA.press_back()
        assert self.userA.find_text_by_ocr("Qobuz", timeout=8) is not None, (
            "奖项弹层关闭后未停留 Qobuz 主页(导航栈变化)")
        self.userA.assert_no_auth_error()
