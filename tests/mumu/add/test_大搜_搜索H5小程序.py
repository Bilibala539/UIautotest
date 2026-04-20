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
        - 实例化用户（无需 login，框架自动管理）
        """
        self.userA = self.users("userA")

    def test_search_H5(self):

        self.userA.search(text="移动开门", isclose=False)
        self.userA.click_image(SEARCH_RESULT_OPEN_DOOR, region=Normal.HALF_UP)
        time.sleep(5)
        self.userA.click_text("取消", region=Normal.CENTER_POP)
        self.userA.image_exists(OPEN_DOOR_LOGO, region=Normal.HALF_UP)
        self.userA.click_image(OPEN_DOOR_CLOSE, region=Normal.HALF_UP)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        """
        测试后清理（框架自动关闭 POPO，无需手动 logout）
        """
        pass
