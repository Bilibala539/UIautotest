"""
测试用例: 打开个人中心-用户名和签名超过一行-有徽章-有电子工卡-有侧边栏
功能点: 侧边栏tab
操作步骤: 打开个人中心，验证侧边栏显示正常
预期结果: 服务按照正确顺序排列，存在侧边tab导航栏
"""
from conftest import BaseTest


class TestSidebarFullDisplay(BaseTest):
    """侧边栏完整显示验证"""

    def setup(self):
        self.userA = self.users("userA")

    def test_sidebar_full_display(self):
        """
        步骤:
        1. 打开侧边栏
        2. 验证"我的收藏"存在
        3. 验证"设置"存在
        4. 验证"登录设备管理"存在
        5. 关闭侧边栏
        """
        self.userA.open_sidebar()
        self.userA.text_exists("我的收藏")
        self.userA.text_exists("登录设备管理")
        self.userA.text_exists("设置")
        self.userA.close_sidebar()

    def teardown(self):
        pass
