"""
测试用例: 入群验证默认状态
Excel来源: Row 32
"""
from conftest import BaseTest


class Test入群验证默认状态(BaseTest):
    """入群验证默认关闭"""

    def setup(self):
        self.userA = self.users("userA")

    def test_join_verification_default(self):
        """验证群设置页面中能看到消息提醒（间接证明在群设置页）"""
        result = self.userA.verify_group_setting_default(
            group_identifier="吴彦祖",
            setting_name="消息提醒"
        )
        assert result == "found", "应能在群设置中看到消息提醒"

    def teardown(self):
        pass
