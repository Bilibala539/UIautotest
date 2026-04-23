"""
测试用例: 应用外分享
探索来源: AI自主探索POPO App生成
探索补全: 系统分享Intent→选择POPO→选联系人→确认发送
"""
from conftest import BaseTest


class TestShareImageFromExternal(BaseTest):
    """应用外分享图片到POPO功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_share_image_from_external(self):
        """
        测试从系统相册分享图片到POPO

        步骤:
        1. 触发系统截图确保有可分享的图片
        2. 通过ACTION_SEND Intent触发系统分享选择器
        3. 选择"网易POPO"
        4. 在POPO中选择"发送给同事或群组"
        5. 选择 grp.popoqa50 联系人
        6. 确认发送
        7. 返回消息列表
        """
        self.userA.share_image_from_external(recipient="grp.popoqa50")

    def teardown(self):
        pass
