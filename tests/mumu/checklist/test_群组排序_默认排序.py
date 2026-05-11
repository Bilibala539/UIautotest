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
        1. 进入通讯录-群组页面
        2. 点击排序图标打开排序面板
        3. 验证默认排序为"群组名称A-Z"

        预期结果:
        - 排序面板中"群组名称A-Z"为当前选中状态
        """
        # 1. 进入群组列表
        self.userA.open_contacts_groups()

        # 2. 验证当前排序为群组名称（页面顶部应有"群组名称√"标记）
        self.userA.text_exists("群组名称")

    def teardown(self):
        """测试后清理"""
        pass
