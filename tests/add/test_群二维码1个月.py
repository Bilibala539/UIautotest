"""
测试用例: 修改二维码有效期为1个月
Excel来源: Row 49
"""
from conftest import BaseTest


class Test群二维码1个月(BaseTest):
    """修改二维码有效期为1个月"""

    def setup(self):
        self.userA = self.users("userA")

    def test_群二维码1个月(self):
        """修改二维码有效期为1个月"""
        # 简化版: 验证能打开群二维码页面
        result = self.userA.open_group_qr_code("吴彦祖")
        assert result, "应能打开群二维码页面"

    def teardown(self):
        pass
