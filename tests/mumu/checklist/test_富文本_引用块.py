"""
测试用例: 富文本-引用块消息
探索来源: AI自主探索POPO App富文本编辑功能
探索记录: explorer_output/records/exploration_record_richtext.md
"""
from conftest import BaseTest


class TestRichTextQuoteBlock(BaseTest):
    """富文本引用块消息测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户A
        - 用户A登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_send_quote_message(self):
        """
        测试场景: 使用Markdown引用语法发送引用块消息

        步骤:
        1. 搜索联系人进入聊天页面
        2. 点击段落按钮进入扩展编辑模式
        3. 滑动工具栏找到Markdown按钮
        4. 切换到Markdown模式
        5. 输入引用语法 (> 引用内容)
        6. 点击发送按钮
        7. 验证消息发送成功

        预期结果:
        - 成功切换到Markdown编辑模式
        - 引用语法正确解析
        - 消息发送成功，显示为引用块样式
        """
        result = self.userA.send_quote_message(
            recipient="grp.popoqa93",
            text="引用块测试消息"
        )
        assert result, "引用块消息发送应该成功"

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
