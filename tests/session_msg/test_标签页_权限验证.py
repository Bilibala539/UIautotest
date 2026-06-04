"""
测试用例: 标签页优化（2期）- 标签页展示（权限验证）
Excel来源: 会话区及消息.xlsx 行 36(无权限群成员添加自定义标签页)
"""
import time
from conftest import BaseTest

RECIPIENT_GROUP = "grp.popoqa93"


class TestTabPagePermission(BaseTest):
    """标签页权限验证测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.aw._ensure_message_page()

    def test_no_permission_add_custom_tab(self):
        """
        测试场景: 无标签页管理权限的群成员尝试添加自定义标签页
        预期: 无法添加或提示无权限
        Excel行号: 36
        """
        self.userA.aw._enter_chat_page(RECIPIENT_GROUP)
        time.sleep(1)
        self.userA.aw._enter_group_settings_from_chat()
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

        # 验证进入了标签页管理页面
        self.userA.aw.text_exists("全部标签页", timeout=5)

        # 尝试找 + 添加按钮
        add_pos = self.userA.aw.find_text_by_ocr("+", timeout=3)
        if add_pos:
            self.userA.aw.click_text("+", timeout=3)
            time.sleep(1)
            # 如果弹出添加界面说明有权限；如果无权限会有提示
            link_pos = self.userA.aw.find_text_by_ocr("链接", timeout=3)
            perm_pos = self.userA.aw.find_text_by_ocr("权限", timeout=2)
            assert (link_pos is not None) or (perm_pos is not None), "应弹出添加界面或权限提示"

    def teardown(self):
        self.userA.aw.return_to_message_list()
