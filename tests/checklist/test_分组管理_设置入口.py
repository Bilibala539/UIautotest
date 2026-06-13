"""
测试用例: 分组管理页面
功能点: 验证可进入分组管理页面
操作步骤: 打开会话分组面板 → 点击"管理" → 进入管理分组页面
预期结果: 成功进入管理分组页面，分组列表显示正常
"""
import time
from conftest import BaseTest


class TestGroupManageSettings(BaseTest):
    """分组管理-设置按钮"""

    def setup(self):
        self.userA = self.users("userA")

    def test_group_manage_page_accessible(self):
        """
        步骤:
        1. 打开会话分组面板
        2. 点击"管理"进入分组管理页面（内部使用 click_image + find_text_by_ocr）
        3. 验证已进入管理分组页面
        """
        # open_session_group_manage 内部流程：打开分组面板 → 点击"管理" → 验证"管理分组"
        result = self.userA.aw.open_session_group_manage()
        time.sleep(1)
        assert result, "进入分组管理页面失败"

    def teardown(self):
        """返回消息列表"""
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
