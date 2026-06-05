"""
测试用例: 消息历史-云文档
探索来源: AI自主探索POPO App生成
探索补全: 原始用例步骤模糊，通过自主探索App补全操作路径
"""
from conftest import BaseTest


class TestMessageHistoryCloudDocs(BaseTest):
    """消息历史-云文档测试类"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_view_cloud_docs_in_message_history(self):
        """
        测试场景: 在群设置的消息历史中查看云文档
        预期结果: 显示云文档分类，按照消息发送时间倒序排序

        操作路径: 消息列表→搜索群组→进入聊天→群设置→云文档Tab
        """
        result = self.userA.view_message_history_cloud_docs("grp.popoqa")
        assert result, "查看消息历史-云文档应该成功"

    def teardown(self):
        """测试后清理"""
        pass
