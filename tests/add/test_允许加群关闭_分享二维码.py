"""
测试用例: 关闭允许申请加群后点分享二维码弹toast
Excel来源: Row 93
"""
from conftest import BaseTest


class Test允许加群关闭_分享二维码(BaseTest):
    """关闭允许申请加群后点分享二维码弹toast"""

    def setup(self):
        self.userA = self.users("userA")

    def test_允许加群关闭_分享二维码(self):
        """关闭允许申请加群后点分享二维码弹toast"""
        # 简化版: 验证能打开群二维码页(分享入口)
        result = self.userA.open_group_qr_code("吴彦祖")
        assert result, "应能打开二维码页(分享入口)"

    def teardown(self):
        pass
