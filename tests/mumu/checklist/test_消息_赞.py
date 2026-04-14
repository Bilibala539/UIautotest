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

    def test_send_p2p_message_good(self):
        self.userA.search_people(text="grp.popoqa50", isgoin=True)
        self.userA.click_image(MSG_GOOD)
        self.userA.image_exists(MSG_MESSAGE_GOOD, timeout=15)
        self.userA.recall_message(is_good=True)

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        try:
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()
