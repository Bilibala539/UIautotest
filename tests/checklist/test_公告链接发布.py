"""
测试用例: 输入链接内容并发布
Excel来源: Row 79
"""
from conftest import BaseTest


class Test公告链接发布(BaseTest):
    """输入链接内容并发布"""

    def setup(self):
        self.userA = self.users("userA")

    def test_公告链接发布(self):
        """输入链接内容并发布"""
        import time
        content = f"https://example.com/test_{int(time.time())}"
        result = self.userA.set_group_announcement("吴彦祖", content)
        assert result, "链接公告应该发布成功"

    def teardown(self):
        pass
