"""
测试用例: 关闭会话分组页面-点击左上角返回
功能点: 在管理分组页面点击左上角返回按钮，返回上一页（会话设置页面）
操作步骤: 进入管理分组页面后点击左上角返回
预期结果: 返回会话设置页面
"""
import time
from conftest import BaseTest


class TestCloseGroupPageBack(BaseTest):
    """关闭分组页面-返回按钮"""

    def setup(self):
        self.userA = self.users("userA")

    def test_close_group_page_via_back(self):
        """
        步骤:
        1. 进入分组管理页面
        2. 点击左上角返回按钮（物理返回键模拟）
        3. 验证返回到消息列表或会话设置页面
        """
        # 进入分组管理页面
        self.userA.aw.open_session_group_manage()
        time.sleep(1)

        # 点击返回
        self.userA.aw.press_back()
        time.sleep(1)

        # 验证已离开分组管理页面（不再显示"管理分组"标题）
        result = self.userA.aw.find_text_by_ocr("管理分组", timeout=2)
        assert result is None, "未成功返回，仍在管理分组页面"

    def teardown(self):
        """确保回到消息列表"""
        self.userA.aw.press_back()
        time.sleep(0.5)
        # 尝试关闭可能存在的面板
        close_pos = self.userA.aw.find_text_by_ocr("收起", timeout=2)
        if close_pos:
            self.userA.aw.tap(close_pos[0], close_pos[1])
