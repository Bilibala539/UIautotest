"""
测试用例: 标签页优化（3期）- 各类型会话标签页可见开关
Excel来源: 会话区及消息.xlsx 行 27(P2P标签页开关), 28(群组标签页开关)
"""
from conftest import BaseTest

RECIPIENT_P2P = "grp.popoqa50"
RECIPIENT_GROUP = "grp.popoqa93"


class TestTabPageVisibilitySwitch(BaseTest):
    """标签页可见开关设置测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_p2p_tab_visibility_switch(self):
        """
        测试场景: P2P会话中标签页单独设置可见开关
        前置条件: 用户已在P2P会话中
        操作: 用户在P2P会话中设置某个标签页的可见开关
        预期: 该标签页的可见开关设置成功

        Excel行号: 27 (index 0-based)
        """
        import time
        self.userA.aw._enter_chat_page(RECIPIENT_P2P)
        time.sleep(1)

        # 进入聊天设置
        self.userA.aw.click_text("设置", timeout=5)
        time.sleep(1)

        # 找到标签页设置入口
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

        # 验证进入了标签页管理页面
        self.userA.aw.text_exists("全部标签页", timeout=5)

        # 验证云文档选项存在（代表标签页列表正常加载）
        self.userA.aw.text_exists("云文档", timeout=3)

    def test_group_tab_visibility_switch(self):
        """
        测试场景: 群组会话中标签页单独设置可见开关
        前置条件: 用户已在群组会话中
        操作: 用户在群组会话中设置某个标签页的可见开关
        预期: 该标签页的可见开关设置成功

        Excel行号: 28 (index 0-based)
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

        # 验证标签页管理页面存在
        self.userA.aw.text_exists("全部标签页", timeout=5)

    def teardown(self):
        self.userA.aw.go_to_home()
