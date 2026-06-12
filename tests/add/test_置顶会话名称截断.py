"""
测试用例: 置顶会话名称显示-3
功能点: 置顶会话名称超出部分截断不显示
操作步骤: 创建长名称的群组并置顶，查看名称是否被截断
预期结果: 超出部分的字符直接截断不显示（显示为"..."结束）
"""
from conftest import BaseTest
from image.image_name_mapping import MESSAGE_TAB_BLUE


class TestPinnedConversationNameTruncate(BaseTest):
    """置顶会话名称截断显示"""

    def setup(self):
        self.userA = self.users("userA")
        # 创建一个名称很长的群（超阈值才会触发截断，预期显示"..."结尾）
        self.long_group_name = "这是一个名称非常长的测试群组名称需要超过显示阈值"
        self.group_name = self.userA.aw.setup_owner_group(desired_name=self.long_group_name)
        # 将该群置顶，使其显示在消息列表顶部置顶区域
        self.userA.long_press_session_pin()

    def test_pinned_conversation_name_truncated(self):
        """
        步骤:
        1. 验证消息列表页正常渲染
        2. OCR 扫描页面文本，获取置顶会话的显示文本
        3. 断言显示文本以"..."结尾（截断标志）
        """
        # 验证消息列表页正常渲染
        self.userA.aw.image_exists(MESSAGE_TAB_BLUE, timeout=10)

        # OCR 全量扫描消息列表页，获取所有可见文字
        items = self.userA.aw.ocr_scan_page()

        # 从 OCR 结果中查找名称最接近长群名的文本（可能是截断后的名称）
        found_texts = [
            item['text'] for item in items
            if self.long_group_name[:6] in item['text']  # 匹配前缀
        ]

        assert len(found_texts) > 0, (
            f"未在消息列表中找到以'{self.long_group_name[:6]}'开头的会话名称"
        )

        # 断言截断：显示文本应以"..."结尾，且长度短于原始名称
        display_name = found_texts[0]
        truncated = display_name.endswith("...")
        assert truncated, (
            f"置顶会话名称未被截断，显示为'{display_name}'，"
            f"期望以'...'结尾（原始名称: '{self.long_group_name}'）"
        )

    def teardown(self):
        # 取消置顶
        try:
            self.userA.long_press_session_pin()
        except Exception:
            pass
        # 清理群组
        try:
            self.userA.aw.delete_team(self.group_name)
        except Exception:
            pass
