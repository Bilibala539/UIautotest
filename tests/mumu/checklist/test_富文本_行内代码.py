"""
测试用例: 富文本-行内代码消息
探索来源: AI自主探索POPO App富文本编辑功能
探索记录: explorer_output/records/exploration_record_richtext.md
"""
from conftest import BaseTest


class TestRichTextInlineCode(BaseTest):
    """富文本行内代码消息测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户A
        - 用户A登录
        """
        self.userA = self.users("userA")

    def test_send_inline_code_message(self):
        """
        测试场景: 使用Markdown行内代码语法发送行内代码消息

        步骤:
        1. 搜索联系人进入聊天页面
        2. 点击段落按钮进入扩展编辑模式
        3. 滑动工具栏找到Markdown按钮
        4. 切换到Markdown模式
        5. 输入行内代码语法 (`代码内容`)
        6. 点击发送按钮
        7. 验证消息发送成功

        预期结果:
        - 成功切换到Markdown编辑模式
        - 行内代码语法正确解析
        - 消息发送成功，代码以行内样式显示
        """
        result = self.userA.send_inline_code_message(
            recipient="grp.popoqa93",
            text="print(hello)"
        )
        assert result, "行内代码消息发送应该成功"

    def teardown(self):
        pass
