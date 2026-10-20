# CASE-ID: music-NEG-009
"""Swan 回归·M07 平台入口:平台页离线→余额卡回退默认 0.000000(music-NEG-009)。

步骤→AW 映射(7.1 通用,断网维度,行为记录类):
  1. 平台页正常加载记基线 → go_bottom_tab("平台") + platform_row_state
     行锚就绪 + text_not_exists("0.000000")(余额非零前置的基线反证)
  2. 开飞行模式 → toggle_airplane_mode(系统设置页 OCR 点开关,框架无
     网络开关 API 的唯一通道)→ 回宿主 swipe_down 下拉刷新 →
     text_exists("0.000000")(getUserSumMoney 离线回退默认值)
  3. 恢复网络 → 再 toggle 一次 → 刷新 → text_not_exists("0.000000")
     (余额恢复真实值)+ 行锚仍在(列表恢复,自愈不崩溃)

cleanup: 网络恢复在正文内完成;teardown 按 _m07_airplane_on 旗标防御性
再切换一次(仅当正文在"已切飞行模式→恢复"之间失败时才动作,防系统态
残留拖垮后续用例)。
B 标定说明:「飞行模式」开关行 OCR 锚与余额卡 0.000000 文字锚待真机
补截精确定位图,见 package_report.json template_needs。
"""

from __future__ import annotations

from conftest import BaseTest


class TestMusicNeg009OfflineBalanceFallback(BaseTest):
    """离线余额卡静默降级 0.000000、恢复网络自愈(行为记录)。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        # 用例私有清理:仅当正文失败于"已开飞行模式→未恢复"区间才切换
        if getattr(self, "_m07_airplane_on", False):
            self.userA.toggle_airplane_mode()
            self._m07_airplane_on = False

    def test_offline_balance_fallback_and_heal(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:基线态——平台页加载 + 余额卡非回退默认值
        state = self.userA.platform_row_state("netease")
        assert state, "平台页基线未加载(平台行锚 [OCR] 未命中)"
        self.userA.text_not_exists("0.000000", timeout=4)
        # 步骤 2:开飞行模式 → 下拉刷新 → 余额卡回退 0.000000
        self.userA.toggle_airplane_mode()
        self._m07_airplane_on = True
        self.userA.swipe_down(400)
        self.userA.text_exists("0.000000", timeout=15)
        # 步骤 3:恢复网络 → 刷新 → 余额恢复真实值、列表自愈
        self.userA.toggle_airplane_mode()
        self._m07_airplane_on = False
        self.userA.swipe_down(400)
        self.userA.text_not_exists("0.000000", timeout=15)
        self.userA.assert_any_text(("网易云", "QQ音乐", "酷狗音乐"), timeout=8)
