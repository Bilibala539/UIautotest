# CASE-ID: ai-POS-014
"""Swan 回归·AI 助手域：管理页多选模式进出与删除控件存在性（ai-POS-014）。

步骤 → AW 映射：
1. 进入角色管理页 → go_top_tab("AI") + mixin open_ai_roles_page
2. 点击多选入口进入多选模式 → click_text("多选")（wave5 实测：多选 ↔
   取消 切换，零自定义角色也可进入）
3. 全选与删除控件存在性（仅存在性——⛔ 删除不可逆禁区 2，零点击零确认）
   → 断言「取消」「全选」「删除」出现
4. 退出多选模式返回 → click_text("取消") 断言「多选」态回归（零删除触发
   角色无变化），press_back 回 AI 首页画廊锚

说明：基线账号无自定义角色，多选目标以系统角色行呈现（YAML SKIP-DATA
降级口径——系统角色只读态另行断言）。

cleanup：无（零删除零写；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiRolesMultiselectMode(SwanRM09Mixin, BaseTest):
    """管理页多选模式进出与删除控件存在性（删除零触发）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_roles_multiselect_enter_exit(self):
        """多选模式进出顺畅，全选/删除控件出现，零删除触发。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_roles_page()

        # 进入多选模式：多选 ↔ 取消 切换 + 全选/删除控件出现
        self.userA.click_text("多选", timeout=10)
        assert self.userA.text_exists("取消", timeout=8) is not None, (
            "点击多选后未进入多选模式（「取消」未出现）[OCR]")
        assert self.userA.text_exists("全选", timeout=8) is not None, (
            "多选模式「全选」控件未出现 [OCR]")
        assert self.userA.text_exists("删除", timeout=8) is not None, (
            "多选模式「删除」控件未出现 [OCR]")  # ⛔ 仅存在性断言，绝不点击

        # 退出多选模式：多选态回归，删除控件消失（零触发）
        self.userA.click_text("取消", timeout=10)
        assert self.userA.text_exists("多选", timeout=8) is not None, (
            "点击取消后未退出多选模式（「多选」态未回归）[OCR]")
        assert self.userA.find_text_by_ocr("删除", timeout=3) is None, (
            "退出多选模式后「删除」控件仍可见（模式未真正退出）[OCR]")

        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
