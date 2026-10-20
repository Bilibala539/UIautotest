# CASE-ID: library-NEG-045
"""Swan 回归·M12 收藏与曲库：平台授权失败码映射容错（library-NEG-045，ADD1 复审改判 B 转，部分转换）。

用例 → AW 映射（前置：至少一个第三方平台未授权；禁区 8——只验证弹窗
与失败路径，不真授权，立即取消）：
- S1 未授权平台段触发授权入口：酷狗/Apple Music 段 click_text →
  授权按钮（去授权/立即授权 候选）点击。
- S2 授权进度弹窗拉起：断言 取消/进度/授权中 任一命中（应用内弹层，
  无 SDK 流跳转——POS-018 同族口径）。
- S3 立即取消 + 失败码映射提示采样：click_any_text(取消/关闭) →
  取消码提示文案（已取消/失败 类）OCR 采样探测，命中与否记录不硬断言
  （文案未核准，执行轮校准登记 template_needs）；硬断言为平台仍未授权
  （去授权/立即授权 再命中）且段切换无崩溃。
- S4-S5 降级注记：SDK 拒绝拉起与跳商店静默分支为设备现状采样面（依赖
  真实 SDK 行为），未纳入自动化，见 package_report.notes。
清理：未授权态零变更（取消路径），无数据清理。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin
from image.image_name_mapping import SWAN_PLAYLIST_TAB_SWAN


class TestLibraryNeg045AuthFailCodeTolerance(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """授权失败码映射容错：拉起进度弹窗后立即取消，平台保持未授权。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_auth_fail_code_tolerance(self):
        """授权弹窗拉起即取消，失败态保持，取消码提示采样记录。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1：未授权平台段 + 授权入口
        seg = self.userA.probe_any_text(('Apple Music', '酷狗'), timeout_each=3)
        assert seg is not None, "歌单页未见未授权平台 Tab（Apple Music/酷狗）"
        self.userA.click_text(seg, timeout=5)
        btn = self.userA.probe_any_text(('去授权', '立即授权', '授权'), timeout_each=3)
        assert btn is not None, f"{seg} 段未见授权入口"
        self.userA.click_text(btn, timeout=5)
        # S2：授权进度弹窗拉起（应用内，无 SDK 流跳转）
        assert self.userA.probe_any_text(
            ('取消', '进度', '授权中'), timeout_each=3) is not None, (
            "授权进度弹窗未出现（可能直接跳转 SDK 流，执行轮校准）")
        # S3：立即取消 + 失败码提示采样（不硬断言）+ 未授权态保持
        self.userA.click_text_candidates(('取消', '关闭', '暂不'), timeout_each=3)
        self.userA.probe_any_text(('已取消', '取消授权', '失败'), timeout_each=2)
        assert self.userA.probe_any_text(
            ('去授权', '立即授权'), timeout_each=3) is not None, (
            "取消后未回到未授权态（失败码映射分支失守）")
        self.userA.image_exists(SWAN_PLAYLIST_TAB_SWAN, timeout=8)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（未授权态零变更）。"""
        pass
