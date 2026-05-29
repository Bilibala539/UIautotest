
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCreateTeam(BaseTest):

    def setup(self):
        """
        测试前初始化
        - 实例化用户（无需 login，框架自动管理）
        """
        self.userA = self.users("userA")

    def test_search_KM(self):
        """
        """
        self.userA.search(text="KM", isclose=False)
        self.userA.image_exists(SEARCH_RESULT_KM, region=Normal.HALF_UP)
        self.userA.click_image(KM_ICON, region=Normal.HALF_UP)
        time.sleep(5)
        self.userA.click_image(KM_LOGO, region=Normal.HALF_UP)

    def teardown(self):
        """
        测试后清理（框架自动关闭 POPO，无需手动 logout）
        """
        pass
