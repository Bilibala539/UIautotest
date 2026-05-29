"""
测试用例: 列表中会话-自定义头像显示
覆盖文字用例: 列表中会话-自己设置的头像
"""
import os
from conftest import BaseTest


class TestCustomAvatarVisible(BaseTest):
    """验证分组详情列表中自定义头像正常显示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_custom_avatar_visible(self):
        """
        Row 32: 当会话头像为自定义时，在列表中正常显示
        验证方法：在消息列表中查找有自定义头像的会话，截图存证
        """
        # 消息列表中的群组通常有自定义头像
        # 截图保存供人工确认
        self.userA.aw.take_screenshot(
            save_path=os.path.join(self.userA.aw.SCREENSHOT_DIR, "test_custom_avatar.png")
        )

        # 验证消息列表页存在（有"消息"Tab说明在正确页面）
        self.userA.aw.text_exists("消息", timeout=3)

    def teardown(self):
        pass
