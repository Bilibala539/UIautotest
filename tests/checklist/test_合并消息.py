"""
测试用例: 合并消息（合并转发）
探索来源: AI自主探索POPO App生成
探索补全: 发消息→长按→多选→合并转发→选联系人→验证合并消息卡片
"""
from conftest import BaseTest


class TestMergeForwardMessage(BaseTest):
    """合并转发消息功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_merge_forward_message(self):
        """
        测试合并转发消息功能

        步骤:
        1. 发送一条消息到 grp.popoqa50，留在聊天页面
        2. 长按该消息，点击多选
        3. 点击合并转发
        4. 在转发选人页面搜索并选择 grp.popoqa50
        5. 验证已发送 toast 出现
        6. 验证合并消息卡片出现（含"聊天记录"文案）
        7. 返回消息列表
        """
        message = self.userA.send_message(recipient="grp.popoqa50", isback=False)
        self.userA.merge_forward_message(message, forward_to="grp.popoqa50")
        self.userA.aw.press_back()

    def teardown(self):
        pass
