"""
测试用例: 多选消息功能
探索来源: AI自主探索POPO App生成
"""
from conftest import BaseTest


class TestMultiSelectMessage(BaseTest):
    """多选消息功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_multi_select_message(self):
        """
        测试多选消息功能

        步骤:
        1. 发送一条消息，留在聊天页面
        2. 长按该消息，点击多选
        3. 验证进入多选模式
        4. 退出多选模式
        5. 返回消息列表
        """
        message = self.userA.send_message(recipient="grp.popoqa93", isback=False)
        self.userA.multi_select_message(message)
        self.userA.aw.press_back()

    def teardown(self):
        pass
