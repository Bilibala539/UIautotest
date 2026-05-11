"""
测试用例: 侧边栏编辑功能
对应Excel用例: Row 74 - 侧边栏tab - 侧边栏编辑
"""
from conftest import BaseTest


class TestSidebarEdit(BaseTest):
    """侧边栏编辑功能测试"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_sidebar_edit_entry(self):
        """
        测试场景: 打开个人中心，点击更多应用的编辑
        
        步骤:
        1. 在消息列表页点击底部"更多"Tab
        2. 查看更多应用面板
        3. 验证存在"编辑"按钮

        预期结果:
        - 更多应用面板显示
        - 编辑按钮可见
        """
        # 1. 点击更多Tab
        self.userA.click_text("更多")

        # 2. 验证更多应用面板出现
        self.userA.text_exists("更多应用")

        # 3. 验证编辑按钮存在
        self.userA.text_exists("编辑")

    def teardown(self):
        """测试后清理"""
        pass
