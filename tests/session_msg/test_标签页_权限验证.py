"""
测试用例: 标签页优化（2期）- 标签页展示（权限验证）
Excel来源: 会话区及消息.xlsx 行 36(无权限群成员添加自定义标签页)
注: 行35(P2P添加自定义标签页)已有 test_P2P添加自定义标签页.py 覆盖，此处仅补权限用例
"""
from conftest import BaseTest

RECIPIENT_GROUP = "grp.popoqa93"


class TestTabPagePermission(BaseTest):
    """标签页权限验证测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_no_permission_add_custom_tab(self):
        """
        测试场景: 无标签页管理权限的群成员尝试添加自定义标签页
        操作: 进入群组会话设置页面，点击添加自定义标签页
        预期: 无法添加自定义标签页，提示无权限

        Excel行号: 36 (index 0-based)
        注意: 需要使用非群主/管理员身份进入群组
        """
        import time
        self.userA.aw._enter_chat_page(RECIPIENT_GROUP)
        time.sleep(1)

        # 进入群设置
        self.userA.aw.click_text("设置", timeout=5)
        time.sleep(1)

        # 找到标签页
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

        # 尝试点击 + 添加按钮
        add_pos = self.userA.aw.find_text_by_ocr("+", timeout=5)
        if add_pos:
            self.userA.aw.click_text("+", timeout=5)
            time.sleep(1)
            # 验证无权限提示
            no_perm = self.userA.aw.find_text_by_ocr("权限", timeout=3)
            assert no_perm is not None, "非管理员添加标签页应提示无权限"
        else:
            # 如果连 + 按钮都不显示，说明无权限（也算通过）
            pass

    def teardown(self):
        self.userA.aw.go_to_home()
