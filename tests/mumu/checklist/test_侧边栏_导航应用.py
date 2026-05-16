"""
测试用例: 侧边导航栏存在应用入口
功能点: 打开个人中心侧边栏，验证至少显示一个功能入口（我的收藏/登录设备管理/设置/服务台）
操作步骤: 打开个人中心，查看侧边栏中的功能入口
预期结果: 侧边栏显示正常，存在至少一个功能入口
"""
import time
from conftest import BaseTest
from image.image_name_mapping import (
    SIDEBAR_MY_COLLECTION,
    SIDEBAR_DEVICE_MANAGEMENT,
    SIDEBAR_SETTINGS_BUTTON,
    SIDEBAR_SERVICE_DESK,
)


class TestSidebarNavApp(BaseTest):
    """侧边导航栏应用显示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_sidebar_nav_has_app(self):
        """
        步骤:
        1. 打开侧边栏
        2. 验证侧边栏中存在至少一个功能入口
        """
        # 打开侧边栏（内部已通过 image_exists 校验侧边栏打开）
        self.userA.open_sidebar()
        time.sleep(1)

        # 逐一检测侧边栏中的功能入口图片（至少一个存在）
        entries = [
            SIDEBAR_MY_COLLECTION,
            SIDEBAR_DEVICE_MANAGEMENT,
            SIDEBAR_SETTINGS_BUTTON,
            SIDEBAR_SERVICE_DESK,
        ]
        found = [img for img in entries if self.userA.aw.find_image(img, timeout=2)]

        assert len(found) > 0, (
            f"侧边栏中未找到任何功能入口图片。"
            f"已检测: 我的收藏/登录设备管理/设置/服务台"
        )

        # 关闭侧边栏
        self.userA.aw.press_back()

    def teardown(self):
        pass
