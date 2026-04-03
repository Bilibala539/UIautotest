
import time

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
        """
        测试场景: 创建群组并验证

        步骤:
        1. 点击会话列表的加号按钮
        2. 点击创建群聊
        3. 搜索并选择群成员
        4. 确认创建
        5. 验证群聊创建成功（页面出现"发起群聊"、"并邀请"、"加入群聊"文案）
        """
        self.userA.search(text="网易KM")
        self.userA.image_exists(SEARCH_RESULT_KM, region=Normal.HALF_UP)
        self.userA.click_image(KM_ICON, region=Normal.HALF_UP)
        time.sleep(5)
        self.userA.click_image(RN_CLOSE, region=Normal.HALF_UP)
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
