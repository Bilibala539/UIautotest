# CASE-ID: ai-POS-020
"""Swan 回归·AI 助手域：编辑器不保存返回零写（ai-POS-020）。

步骤 → AW 映射：
1-2. 进入新建角色编辑器并输入部分字段 → go_top_tab("AI") +
     mixin open_ai_role_editor() + 点占位提示聚焦 + input_text——
     YAML 数据「QA正-草稿0928」为中文，adb 注入不可达，以 ASCII 等价
     「QA-draft-0928」替代（仅输入不保存）
3. 不点保存直接返回 → press_back 收键盘 → press_back 退出（若出现确认
     弹层以返回键取消，零提交）→ 画廊锚回归（无保存确认弹窗阻塞、无崩溃）
4. 核对角色列表零新增 → mixin open_ai_roles_page +
     text_not_exists("QA-draft-0928")（服务端无角色新增的列表级核实）
5. 再次进入新建分型表单为空 → open_ai_role_editor() + 占位提示回归 +
     草稿文本不存在（草稿不跨会话残留）

cleanup：无（未保存不落库，全程零 addOrUpdateRole 提交；冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiEditorNoSaveZeroWrite(SwanRM09Mixin, BaseTest):
    """编辑器不保存返回零写（服务端无角色新增）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_editor_no_save_zero_write(self):
        """不保存返回后列表零新增、重进表单为空。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()

        # 仅输入不保存（ASCII 等价替代 YAML 中文草稿名）
        self.userA.click_text("万事通", timeout=10)
        self.userA.clear_input()
        self.userA.input_text("QA-draft-0928")
        self.userA.press_back()

        # 不点保存直接返回：确认弹层（如有）以返回键取消，零提交
        self.userA.press_back()
        if self.userA.find_text_by_ocr("添加更多AI角色", timeout=5) is None:
            self.userA.press_back()
        self.userA.assert_ai_home_gallery()

        # 角色列表零新增
        self.userA.open_ai_roles_page()
        assert self.userA.text_not_exists("QA-draft-0928", timeout=5), (
            "未保存的草稿角色出现在角色列表（发生了非预期服务端写）[OCR]")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

        # 重进新建分型：表单为空（占位回归 + 草稿零残留）
        self.userA.open_ai_role_editor()
        assert self.userA.text_exists("万事通", timeout=10) is not None, (
            "重进编辑器后昵称占位提示未回归 [OCR]")
        assert self.userA.text_not_exists("QA-draft-0928", timeout=5), (
            "草稿文本跨会话残留（草稿保护行为与零写口径不符）[OCR]")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
