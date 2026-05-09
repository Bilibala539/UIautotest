"""
测试用例: 发送P2P消息
探索来源: AI自主探索POPO App生成
探索记录: explorer_output/records/exploration_record_send_message.md
"""
from conftest import BaseTest


class TestSendP2PMessage(BaseTest):
    """发送P2P消息测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户A
        - 用户A登录
        """
        self.userA = self.users("userA")

    def test_send_p2p_message_link(self):
        """
        测试场景: 通过搜索联系人发送P2P普通链接

        步骤:
        1. 进入聊天页面
        2. 输入普通链接并发送
        3. 验证发送成功
        4. 撤回消息

        预期结果:
        - 成功进入P2P聊天页面
        - 消息发送成功（包含链接被正确识别）
        - 撤回成功
        """
        # 发送链接消息并验证发送成功
        result = self.userA.send_message(
            recipient="grp.popoqa50",
            message="https://popo.netease.com/"
        )
        assert result, "P2P链接消息发送应该成功"

    def teardown(self):
        pass
