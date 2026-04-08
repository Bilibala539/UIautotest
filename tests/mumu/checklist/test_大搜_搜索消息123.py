from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCreateTeam(BaseTest):

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_search_msg(self):
        self.userA.search_msg()

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        try:
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()
