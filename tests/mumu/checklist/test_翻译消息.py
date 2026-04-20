"""
测试用例: 翻译消息功能
探索来源: AI自主探索POPO App生成
"""
from conftest import BaseTest


class TestTranslateMessage(BaseTest):
    """翻译消息功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_translate_message(self):
        """
        测试翻译消息功能

        步骤:
        1. 发送一条消息，留在聊天页面
        2. 长按该消息，点击翻译
        3. 验证翻译结果出现在消息下方
        4. 返回消息列表
        """
        message = self.userA.send_message(recipient="grp.popoqa93", isback=False)
        self.userA.translate_message(message)
        self.userA.aw.press_back()

    def teardown(self):
        pass
