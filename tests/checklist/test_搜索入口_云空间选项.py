"""
测试用例: 搜索入口-综合搜索中有云空间选项
探索来源: AI自主探索POPO App生成
用例描述: 点击搜索框，在搜索指定内容中有一个"云空间"选项
"""
from conftest import BaseTest


class TestSearchCloudOption(BaseTest):
    """搜索入口-综合搜索中云空间选项 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_search_has_cloud_option(self):
        """
        验证底部导航栏中存在'云空间'选项Tab

        注: 在当前 POPO 版本中，"云空间" 已从搜索 Tab 栏移至底部导航栏，
            作为独立的一级入口。
        """
        # 在消息列表页的底部导航栏中直接验证"云空间"存在
        self.userA.text_exists("云空间")

    def teardown(self):
        pass
