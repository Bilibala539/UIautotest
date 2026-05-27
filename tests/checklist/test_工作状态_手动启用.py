"""
测试用例: 手动启用工作状态
功能点: 设置工作状态
操作步骤: 在工作状态页面点击任一状态启用
预期结果: 状态被启用
"""
from conftest import BaseTest


class TestEnableWorkStatus(BaseTest):
    """手动启用工作状态"""

    def setup(self):
        self.userA = self.users("userA")

    def test_enable_work_status(self):
        """
        步骤:
        1. 打开侧边栏 → 点击"工作状态"入口
        2. 点击"忙碌"状态
        3. 验证状态被启用
        """
        self.userA.open_sidebar()
        self.userA.click_text("工作状态", timeout=5)
        import time; time.sleep(1)
        self.userA.click_text("忙碌", timeout=5)
        import time; time.sleep(0.5)
        # 验证状态已启用
        assert self.userA.text_exists("忙碌", timeout=3), "工作状态未成功启用"

    def teardown(self):
        """关闭工作状态页面"""
        self.userA.aw.press_back()
        self.userA.close_sidebar()
