"""
测试用例: 消息设置-启用表情联想 开关控制
探索来源: AI自主探索POPO App消息设置页面生成
"""
from conftest import BaseTest


class TestMsgSettingsEmojiSuggestion(BaseTest):
    """消息设置-启用表情联想 开关测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.open_message_settings()

    def test_toggle_emoji_suggestion(self):
        """
        测试: 切换 启用表情联想 开关

        步骤:
        1. 获取当前开关状态（需滚动页面才可见）
        2. 切换开关到相反状态
        3. 验证状态已改变
        4. 恢复原状态

        预期: 开关可正常开启/关闭
        """
        switch_name = "启用表情联想"

        initial_state = self.userA.get_message_switch_state(switch_name)

        self.userA.set_message_switch(switch_name, not initial_state)
        new_state = self.userA.get_message_switch_state(switch_name)
        assert new_state != initial_state, f"开关 '{switch_name}' 切换后状态应改变"

        self.userA.set_message_switch(switch_name, initial_state)

    def teardown(self):
        pass
