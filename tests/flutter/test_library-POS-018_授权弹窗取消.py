# CASE-ID: library-POS-018
"""Swan 回归·M12 收藏与曲库：授权弹窗拉起与取消路径（library-POS-018，ADD1 复审改判 B 转，部分转换）。

用例 → AW 映射（禁区 8——共享设备不真授权，止步应用内弹层取消）：
- S1 未授权平台段：酷狗/Apple Music 段 click_text 进入（YAML 前置口径：
  未授权段天然空态可替代）。
- S2 点击授权按钮拉起授权确认/进度弹窗：断言 取消/进度/授权中 任一
  命中，EXP 无 SDK 流跳转。
- S3 立即取消：click_any_text(取消/关闭/暂不) → 断言弹层已收、回到
  未授权态（去授权/立即授权 再命中）。
- S4 复核未授权展示：平台 Tab 条 [图] 仍可见（段切换无污染）。
降级注记：SDK 完整流与授权成功态在共享设备禁区（禁区 8），只覆盖
弹层取消主路径；进度弹窗专属标题文案未核准（执行轮采样校准，
template_needs 登记）。
清理：未授权态零变更（取消路径），无数据清理。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin
from image.image_name_mapping import SWAN_PLAYLIST_TAB_SWAN


class TestLibraryPos018AuthSheetOpenCancel(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """授权弹窗拉起与取消路径：止步应用内弹层，取消后保持未授权。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_auth_sheet_open_and_cancel(self):
        """授权按钮拉起应用内弹窗，取消后未授权态保持、无 SDK 流跳转。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1：未授权平台段
        seg = self.userA.probe_any_text(('酷狗', 'Apple Music'), timeout_each=3)
        assert seg is not None, "歌单页未见未授权平台 Tab（酷狗/Apple Music）"
        self.userA.click_text(seg, timeout=5)
        # S2：授权按钮拉起授权确认/进度弹窗
        btn = self.userA.probe_any_text(('去授权', '立即授权', '授权'), timeout_each=3)
        assert btn is not None, f"{seg} 段未见授权入口"
        self.userA.click_text(btn, timeout=5)
        assert self.userA.probe_any_text(
            ('取消', '进度', '授权中'), timeout_each=3) is not None, (
            "授权进度弹窗未出现（可能直接跳转 SDK 流，执行轮校准）")
        # S3-S4：立即取消 → 未授权态保持 → Tab 条无污染
        self.userA.click_text_candidates(('取消', '关闭', '暂不'), timeout_each=3)
        assert self.userA.probe_any_text(
            ('去授权', '立即授权'), timeout_each=3) is not None, (
            "取消后未回到未授权态")
        self.userA.image_exists(SWAN_PLAYLIST_TAB_SWAN, timeout=8)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（未授权态零变更）。"""
        pass
