
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

    def test_create_team(self):

        self.userA.search(text="广州行政助手", isclose=False)
        self.userA.image_exists(SEARCH_RESULT_GZXZZS)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        """
        测试后清理（框架自动关闭 POPO，无需手动 logout）
        """
        pass
