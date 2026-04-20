"""
测试用例: 富文本-字体颜色消息
探索来源: AI自主探索POPO App富文本编辑功能
探索记录: explorer_output/records/exploration_record_richtext.md
"""
from conftest import BaseTest


class TestRichTextFontColor(BaseTest):
    """富文本字体颜色消息测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户A
        - 用户A登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_send_font_color_message(self):
        """
        测试场景: 在扩展编辑模式下发送字体颜色格式消息

        步骤:
        1. 搜索联系人进入聊天页面
        2. 点击段落按钮进入扩展编辑模式
        3. 输入文本内容
        4. 全选文本 (Ctrl+A)
        5. 滑动工具栏找到字色A按钮
        6. 点击字色A按钮应用字体颜色
        7. 点击发送按钮
        8. 验证消息发送成功

        预期结果:
        - 成功进入扩展编辑模式
        - 字体颜色样式应用成功
        - 消息发送成功
        """
        result = self.userA.send_rich_text_message(
            recipient="grp.popoqa93",
            message="字体颜色测试消息",
            format_type="font_color"
        )
        assert result, "字体颜色消息发送应该成功"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        - 停止应用
        """
        try:
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()
