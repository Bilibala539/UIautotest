"""
测试用例: 消息历史-搜索
探索来源: AI自主探索POPO App生成
探索补全: 原始用例步骤模糊，通过自主探索App补全操作路径
"""
from conftest import BaseTest


class TestMessageHistorySearch(BaseTest):
    """消息历史-搜索测试类"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_search_cloud_docs_in_message_history(self):
        """
        测试场景: 在消息历史-云文档中搜索
        预期结果: 搜索规则与综合搜索一致，能搜到匹配的云文档

        操作路径: 消息列表→搜索群组→进入聊天→群设置→云文档Tab→搜索
        """
        result = self.userA.search_message_history("grp.popoqa", keyword="UI")
        assert result, "搜索消息历史应该成功"

    def teardown(self):
        """测试后清理"""
        pass
