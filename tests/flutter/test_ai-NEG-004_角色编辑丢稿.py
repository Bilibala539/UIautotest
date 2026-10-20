# CASE-ID: ai-NEG-004
"""Swan 回归·AI 助手域：角色编辑中途返回丢稿（ai-NEG-004）。

步骤 → AW 映射：
1. AI 首页 → 新建角色编辑器：go_top_tab("AI") + mixin open_ai_role_editor()
2. 填角色名与提示词：点占位提示聚焦输入框（昵称「万事通」/提示词「幽默风趣」）
   + clear_input + input_text——YAML 中文合成文案以 ASCII 等价替代
   （adb 中文输入不可达，框架级限制）
3. 不保存直接返回：press_back 收键盘 → press_back 退出编辑器；
   如出现放弃确认弹层，以返回键取消（绝不点确认/完成——禁区 4
   addOrUpdateRole 服务端写围栏），弹层形态由执行轮如实记录
4. 重进编辑器复核：open_ai_role_editor() 后断言两个占位提示回归（表单为空）
   且草稿文本不存在——无草稿保护、一次性丢稿行为被显式记录

cleanup：无（未保存不落库，全程零服务端角色写；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestRoleEditorDraftLostOnBack(SwanRM09Mixin, BaseTest):
    """角色编辑中途返回丢稿（无草稿确认直接丢失落账）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_role_editor_draft_lost_on_back(self):
        """编辑中途返回丢稿：重进编辑器后占位提示回归、草稿文本零残留。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()

        # 填昵称（点占位提示聚焦）→ 收键盘 → 填提示词（占位提示被键盘遮挡，
        # 须先收键盘再点）
        self.userA.click_text("万事通", timeout=10)
        self.userA.clear_input()
        self.userA.input_text("SynthRole-Neg004")
        self.userA.press_back()
        self.userA.click_text("幽默风趣", timeout=10)
        self.userA.clear_input()
        self.userA.input_text(
            "You are a friendly quiz master who loves fun facts and jokes.")
        self.userA.press_back()

        # 不保存直接返回：若出现放弃确认弹层以返回键取消（零提交），
        # 弹层形态执行轮记录
        self.userA.press_back()
        if self.userA.find_text_by_ocr("添加更多AI角色", timeout=5) is None:
            self.userA.press_back()
        self.userA.assert_ai_home_gallery()

        # 重进复核：表单为空（占位提示回归）且草稿零残留
        self.userA.open_ai_role_editor()
        assert self.userA.text_exists("万事通", timeout=10) is not None, (
            "重进编辑器后昵称占位提示未回归（疑似草稿残留或页面异常）[OCR]")
        assert self.userA.text_exists("幽默风趣", timeout=10) is not None, (
            "重进编辑器后提示词占位提示未回归（疑似草稿残留或页面异常）[OCR]")
        assert self.userA.text_not_exists("SynthRole-Neg004", timeout=5), (
            "未保存的角色名草稿在重进后残留（出现草稿保护行为，与实测丢稿口径不符）[OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
