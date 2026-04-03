"""
测试用例: 创建群组功能测试
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCreateTeam(BaseTest):
    """创建群组功能测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_create_team(self):

        self.userA.search(text="移动开门")
        self.userA.image_exists(SEARCH_RESULT_OPEN_DOOR, region=Normal.HALF_UP)
        self.userA.click_image(OPEN_DOOR_ICON, region=Normal.HALF_UP)
        time.sleep(5)
        self.userA.click_text("取消", region=Normal.MIDDLE)
        self.userA.image_exists(OPEN_DOOR_LOGO, region=Normal.HALF_UP)
        self.userA.click_image(OPEN_DOOR_CLOSE, region=Normal.HALF_UP)
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
