"""
测试用例: 搜索群聊天内容
探索补全: 原始用例步骤模糊，通过自主探索App补全操作路径
探索来源: explorer_output/screenshots/explore2_search_chat_content.png
"""
from conftest import BaseTest


class TestSearchChatContent(BaseTest):
    """搜索群聊天内容功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_search_chat_content(self):
        """
        测试在群设置中搜索聊天内容

        步骤:
        1. 搜索群聊并进入群聊天页
        2. 点击群名称进入群设置
        3. 点击"搜索聊天内容"
        4. 输入搜索关键词"test"
        5. 验证搜索执行成功
        6. 返回消息列表页
        """
        self.userA.search_chat_content(
            group_identifier="grp.popoqa",
            keyword="test"
        )

    def teardown(self):
        pass
