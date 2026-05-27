"""
测试用例: 富文本-背景色消息
探索来源: AI自主探索POPO App富文本编辑功能
探索记录: explorer_output/records/exploration_record_richtext.md
"""
from conftest import BaseTest


class TestRichTextBackgroundColor(BaseTest):
    """富文本背景色消息测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户A
        - 用户A登录
        """
        self.userA = self.users("userA")

    def test_send_background_color_message(self):
        """
        测试场景: 使用Markdown高亮语法发送带背景色的消息

        步骤:
        1. 搜索联系人进入聊天页面
        2. 点击段落按钮进入扩展编辑模式
        3. 滑动工具栏找到Markdown按钮
        4. 切换到Markdown模式
        5. 输入高亮语法 ==文字==
        6. 点击发送按钮
        7. 验证消息发送成功

        预期结果:
        - 成功进入Markdown编辑模式
        - 高亮语法正确解析
        - 消息发送成功，文本带有背景色
        """
        result = self.userA.send_background_color_message(
            recipient="grp.popoqa93",
            text="背景色测试消息"
        )
        assert result, "背景色消息发送应该成功"

    def teardown(self):
        pass
