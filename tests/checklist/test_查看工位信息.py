"""
测试用例: 查看工位信息
探索来源: AI自主探索POPO App生成
用例描述: 进入个人资料页，查看自己工位信息
"""
from conftest import BaseTest


class TestViewWorkStation(BaseTest):
    """查看工位信息 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_view_work_station(self):
        """
        进入个人资料页，查看自己的工位信息
        已有AW: view_my_profile 会采集个人资料各字段
        """
        # 调用已有的查看个人资料方法
        profile = self.userA.view_my_profile()

        # 验证核心字段存在（中文昵称是必有字段）
        assert "nickname_cn" in profile, "个人资料中应包含中文昵称"

    def teardown(self):
        pass
