"""
测试用例: 删除消息
探索补全: 原始用例步骤模糊，通过自主探索App补全操作路径
探索来源: explorer_output/screenshots/explore2_longpress_menu.png
"""
from conftest import BaseTest


class TestDeleteMessage(BaseTest):
    """删除消息功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_delete_message(self):
        """
        测试删除消息功能

        步骤:
        1. 发送一条测试消息，留在聊天页面
        2. 长按该消息，弹出操作菜单
        3. 点击"删除"
        4. 在确认弹窗"确认删除消息"中点击"删除"
        5. 验证消息已被删除
        6. 返回消息列表页
        """
        message = self.userA.send_message(recipient="grp.popoqa93", isback=False)
        self.userA.delete_message(message)
        self.userA.aw.press_back()

    def teardown(self):
        pass
