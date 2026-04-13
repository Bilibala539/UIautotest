"""
测试用例: 发送P2P消息
探索来源: AI自主探索POPO App生成
探索记录: explorer_output/records/exploration_record_send_message.md
"""
import time

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

    def test_send_p2p_textfile(self):
        """
        测试场景: 通过搜索联系人发送P2P文字消息

        步骤:
        1. 在消息页面点击搜索按钮
        2. 搜索 grp.popoqa 联系人
        3. 切换到联系人Tab，点击搜索结果
        4. 进入P2P聊天页面
        5. 发送文件
        """
        file_name = "text"
        self.userA.send_file(file_name=file_name)
        time.sleep(1)
        self.userA.recall_message(file_name)

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
