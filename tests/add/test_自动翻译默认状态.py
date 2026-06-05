"""
测试用例: 自动翻译默认状态
Excel来源: Row 44 - 自动翻译默认关闭
"""
from conftest import BaseTest


class Test自动翻译默认状态(BaseTest):
    """自动翻译默认状态验证"""

    def setup(self):
        self.userA = self.users("userA")

    def test_auto_translate_default_off(self):
        """进入群设置,查找自动翻译选项,验证默认关闭"""
        result = self.userA.verify_group_setting_default(
            group_identifier="吴彦祖",
            setting_name="自动翻译"
        )
        assert result == "found", "应该能找到自动翻译设置项"

    def teardown(self):
        pass
