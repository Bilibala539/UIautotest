
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

    def test_create_team(self):

        self.userA.search(text="阿鱼", isclose=False)
        self.userA.image_exists(SEARCH_RESULT_AYU)
        self.userA.image_exists(SEARCH_ALL_LXR)
        self.userA.image_exists(ICON_FUWUHAO)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        try:
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()
