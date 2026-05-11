"""
测试用例: 侧边导航栏存在1个应用
功能点: 打开个人中心侧边栏，导航栏中显示至少一个应用
操作步骤: 打开个人中心，查看侧边导航栏中的应用
预期结果: 侧边导航栏显示正常，存在至少一个应用图标
"""
import time
from conftest import BaseTest


class TestSidebarNavApp(BaseTest):
    """侧边导航栏应用显示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_sidebar_nav_has_app(self):
        """
        步骤:
        1. 打开侧边栏（向右滑动或点击头像）
        2. 验证侧边栏中存在导航应用（如"日历"、"工作台"等图标或文字）
        """
        # 打开侧边栏
        self.userA.open_sidebar()
        time.sleep(1)

        # 在侧边栏中查找应用入口（常见的有"工作台"、"日历"等）
        # 侧边栏导航通常在左侧竖向排列
        scan_results = self.userA.aw.ocr_scan_page()
        sidebar_texts = [item['text'] for item in scan_results]

        # 验证侧边栏中至少存在一个已知应用
        known_apps = ["日历", "工作台", "邮箱", "云空间", "POPO精选"]
        found_apps = [app for app in known_apps if any(app in t for t in sidebar_texts)]

        assert len(found_apps) > 0, f"侧边栏中未找到任何应用。可见文字: {sidebar_texts[:20]}"

        # 关闭侧边栏
        self.userA.aw.press_back()

    def teardown(self):
        pass
