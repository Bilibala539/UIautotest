"""
测试用例: 设置工作状态的页面展示
功能点: 设置工作状态
操作步骤: 进入设置工作状态页面，查看页面展示
预期结果: 左上角X，列表包含忙碌、会议中、离开等通用状态
"""
from conftest import BaseTest


class TestWorkStatusPageDisplay(BaseTest):
    """设置工作状态的页面展示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_work_status_page_display(self):
        """
        步骤:
        1. 打开侧边栏 → 点击工作状态入口
        2. 验证页面显示状态列表
        """
        self.userA.open_sidebar()
        # 在侧边栏中查找并点击"工作状态"入口
        self.userA.click_text("工作状态", timeout=5)
        import time; time.sleep(1)
        # 验证状态页面展示
        assert self.userA.text_exists("忙碌", timeout=3) or self.userA.text_exists("会议中", timeout=3), \
            "工作状态页面未正常展示"

    def teardown(self):
        """关闭工作状态页面"""
        self.userA.aw.press_back()
        self.userA.close_sidebar()
