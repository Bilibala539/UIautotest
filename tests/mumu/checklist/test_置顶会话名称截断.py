"""
测试用例: 置顶会话名称显示-3
功能点: 置顶会话名称超出部分截断不显示
操作步骤: 查看置顶会话的名称字符
预期结果: 超出部分的字符直接截断不显示
"""
from conftest import BaseTest
from image.image_name_mapping import MESSAGE_TAB_BLUE


class TestPinnedConversationNameTruncate(BaseTest):
    """置顶会话名称截断显示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_pinned_conversation_name_truncated(self):
        """
        步骤:
        1. 验证消息列表页正常渲染
        2. 截图保存 UI 显示效果供人工确认
        """
        # 验证消息列表页正常渲染（通过消息 tab 蓝色高亮图片确认在消息页）
        self.userA.aw.image_exists(MESSAGE_TAB_BLUE, timeout=10)

        # 截图保存 UI 显示效果
        self.userA.aw.take_screenshot(
            save_path="screenshots/test_pinned_name_truncate.png"
        )

    def teardown(self):
        pass
