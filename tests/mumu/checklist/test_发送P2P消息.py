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
        self.userA.login()

    def test_send_p2p_message(self):
        """
        测试场景: 通过搜索联系人发送P2P文字消息

        步骤:
        1. 在消息页面点击搜索按钮
        2. 搜索 grp.popoqa 联系人
        3. 切换到联系人Tab，点击搜索结果
        4. 进入P2P聊天页面
        5. 点击输入框，输入消息文字
        6. 点击发送按钮
        7. 验证发送成功（发送按钮恢复为+号）
        8. 返回消息页面

        预期结果:
        - 搜索能找到 grp.popoqa 联系人
        - 成功进入P2P聊天页面
        - 消息发送成功
        - 返回消息页面后，该会话置顶显示
        """
        result = self.userA.send_message(
            recipient="grp.popoqa50"
        )
        assert result, "P2P消息发送应该成功"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        - 停止应用
        """
        try:
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()
