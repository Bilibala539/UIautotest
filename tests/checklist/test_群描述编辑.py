"""
测试用例: 群主编辑群描述并保存
Excel来源: Row 41
"""
from conftest import BaseTest


class Test群描述编辑(BaseTest):
    """群主编辑群描述并保存"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.setup_owner_group("吴彦祖")

    def test_群描述编辑(self):
        """群主编辑群描述并保存"""
        import time
        # 使用时间戳生成唯一描述内容
        desc = f"自动化测试描述_{int(time.time())}"
        result = self.userA.edit_group_description(
            group_identifier=self.group_name,
            description=desc
        )
        assert result, "群描述应该编辑成功"

    def teardown(self):
        pass
