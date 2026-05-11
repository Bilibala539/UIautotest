"""
测试用例: 打开个人中心-有侧边栏
对应Excel用例: Row 71 - 侧边栏tab - 打开个人中心-有侧边栏
探索补全: 实际App侧边栏内容与原始用例预期有差异，以实际探索结果为准
"""
from conftest import BaseTest


class TestSidebarDisplay(BaseTest):
    """侧边栏展示测试类"""

    def setup(self):
        """
        测试前初始化
        - 获取用户实例（框架自动管理登录和POPO启停）
        """
        self.userA = self.users("userA")

    def test_open_sidebar_display(self):
        """
        测试场景: 打开个人中心，验证侧边栏正常展示
        
        步骤:
        1. 在消息列表页点击左上角头像
        2. 验证侧边栏打开
        3. 验证侧边栏包含关键菜单项

        预期结果:
        - 侧边栏正常打开
        - 包含"帮助与反馈"、"登录设备管理"、"设置"菜单项
        - 页面展示正常
        """
        # 1. 打开侧边栏
        self.userA.open_sidebar()

        # 2. 验证侧边栏关键菜单项存在
        self.userA.text_exists("帮助与反馈")
        self.userA.text_exists("登录设备管理")
        self.userA.text_exists("设置")

        # 3. 关闭侧边栏
        self.userA.close_sidebar()

    def teardown(self):
        """测试后清理（框架自动关闭POPO）"""
        pass
