"""
测试用例: 跳转管理分组页面
功能点: 新增会话分组模块
操作步骤: 分组面板展开后，点击"管理"按钮
预期结果: 进入分组管理页面
"""
from conftest import BaseTest


class TestOpenGroupManagePage(BaseTest):
    """跳转管理分组页面"""

    def setup(self):
        self.userA = self.users("userA")

    def test_open_group_manage_page(self):
        """
        步骤:
        1. 打开会话分组面板
        2. 点击"管理"按钮
        3. 验证进入管理分组页面
        """
        self.userA.open_session_group_panel()
        pos = self.userA.aw.find_text_by_ocr("管理", timeout=5)
        assert pos, "分组面板中未找到'管理'按钮"
        self.userA.aw.tap(pos[0], pos[1])
        import time
        time.sleep(1)
        result = self.userA.aw.find_text_by_ocr("管理分组", timeout=5)
        if not result:
            result = self.userA.aw.find_text_by_ocr("分组管理", timeout=3)
        assert result, "未成功进入管理分组页面"

    def teardown(self):
        self.userA.aw.press_back()
