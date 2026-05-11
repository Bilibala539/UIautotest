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
        测试场景: 切换群组排序为"最后活跃由远及近"
        
        步骤:
        1. 进入通讯录-群组页面
        2. 点击排序图标
        3. 选择"最后活跃由远及近"

        预期结果:
        - 排序切换成功
        - 群组列表按最后活跃时间从远到近排列
        """
        # 1. 进入群组列表
        self.userA.open_contacts_groups()

        # 2. 选择排序方式
        self.userA.select_group_sort_option("最后活跃由远及近")

        # 3. 验证排序已切换
        self.userA.text_exists("最后活跃")

    def teardown(self):
        """测试后清理"""
        pass
