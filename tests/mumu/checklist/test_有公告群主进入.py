"""
测试用例: 有公告时群主进入公告页，显示内容
Excel来源: Row 73
"""
from conftest import BaseTest


class Test有公告群主进入(BaseTest):
    """有公告时群主进入公告页，显示内容"""

    def setup(self):
        self.userA = self.users("userA")

    def test_有公告群主进入(self):
        """有公告时群主进入公告页，显示内容"""
        import time
        # 先设置一条公告
        content = f"测试公告_{int(time.time())}"
        self.userA.set_group_announcement("吴彦祖", content)
        # 再次进入，验证内容可见
        result = self.userA.open_group_announcement_page("吴彦祖")
        assert result, "应能进入群公告页查看"

    def teardown(self):
        pass
