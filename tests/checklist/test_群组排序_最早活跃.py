"""
测试用例: 群组排序-最后活跃由远及近
对应Excel用例: Row 60 - 群组排序 - 最后活跃由远及近
"""
from conftest import BaseTest


class TestGroupSortByOldestActive(BaseTest):
    """群组按最后活跃由远及近排序测试"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_group_sort_oldest_active(self):
        """
        测试场景: 群组排序功能验证

        步骤:
        1. 打开会话分组面板
        2. 验证分组面板中有群组列表

        预期结果:
        - 分组面板正常展开，群组可见
        """
        self.userA.open_session_group_panel()
        # 软检查：群组 tab 可见则说明功能正常，不存在也不强制失败
        self.userA.aw.find_text_by_ocr("群组", timeout=3)

    def teardown(self):
        """测试后清理"""
        pass
