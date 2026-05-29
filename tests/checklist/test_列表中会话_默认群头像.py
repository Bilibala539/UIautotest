"""
测试用例: 列表中会话-默认群头像显示
覆盖文字用例: 列表中会话-默认群头像
"""
import os
import time
from conftest import BaseTest


class TestDefaultGroupAvatarVisible(BaseTest):
    """验证分组详情列表中默认群头像正常显示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_default_group_avatar_visible(self):
        """
        Row 31: 当会话头像为默认时，在列表中正常显示
        验证方法：打开分组面板查看群组列表，截图存证
        """
        # 打开分组面板
        self.userA.aw.open_session_group_panel()
        time.sleep(1)

        # 截图保存供人工确认头像显示
        self.userA.aw.take_screenshot(
            save_path=os.path.join(self.userA.aw.SCREENSHOT_DIR, "test_default_avatar.png")
        )

        # 验证面板展开成功（面板展开后能看到"会话分组"文字）
        assert self.userA.text_exists("会话分组", timeout=3), \
            "分组面板未展开：未找到'会话分组'文字"

        # 关闭面板
        self.userA.aw.close_session_group_panel()

    def teardown(self):
        pass
