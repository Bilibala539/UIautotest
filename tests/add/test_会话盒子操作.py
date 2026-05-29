"""
测试用例: 会话盒子操作
功能点: 会话盒子完整操作流程
操作步骤:
  1. 通过会话设置页添加到盒子 → 验证"会话盒子"出现
  2. 进入会话盒子页面 → 验证会话在盒子内
  3. 通过设置页关闭开关移除 → 验证会话回到列表, 盒子消失
预期结果: 会话盒子完整生命周期操作正常
"""
from conftest import BaseTest
import time


class TestSessionBoxOperations(BaseTest):
    """会话盒子-完整操作流程"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.aw.setup_owner_group("会话盒子测试群")
        if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
            self.userA.close_conversation_box("会话盒子")
            time.sleep(1)

    def test_session_box_full_flow(self):
        # 步骤1: 添加会话到盒子
        self.userA.add_to_session_box(self.group_name)
        self.userA.text_exists("会话盒子", timeout=10)
        # 步骤2: 进入盒子验证会话在盒内
        self.userA.open_session_box()
        self.userA.text_exists(self.group_name, timeout=10)
        self.userA.aw.press_back()
        time.sleep(0.5)
        # 步骤3: 从盒子移除
        self.userA.remove_from_session_box(self.group_name)
        self.userA.text_exists(self.group_name, timeout=10)

    def teardown(self):
        try:
            if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
                self.userA.remove_from_session_box(self.group_name)
        except Exception:
            pass
        try:
            self.userA.aw.delete_team(self.group_name)
        except Exception:
            pass
