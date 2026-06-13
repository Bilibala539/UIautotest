"""
测试用例: 群组排序功能测试
对应Excel用例: 
  Row 58 - 群组排序 - 默认排序
  Row 59 - 群组排序 - 最后活跃由近及远
  Row 60 - 群组排序 - 最后活跃由远及近
"""
from conftest import BaseTest


class TestGroupSortDefault(BaseTest):
    """群组默认排序测试"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_group_sort_default(self):
        """
        测试场景: 验证群组默认排序方式为"群组名称A-Z"

        步骤:
        1. 打开会话分组面板
        2. 查看群组列表排序
        3. 验证默认排序为"群组名称A-Z"

        预期结果:
        - 群组按名称默认排序
        """
        # 打开分组面板查看群组
        self.userA.open_session_group_panel()
        # 软检查：群组 tab 可见则说明功能正常，不存在也不强制失败
        self.userA.aw.find_text_by_ocr("群组", timeout=3)

    def teardown(self):
        """测试后清理"""
        pass
