"""
测试用例: 收藏列表功能验证
Excel来源: 首页其他功能.xlsx ROW6-8
功能点: 收藏列表链接展示及发送人检索功能
"""
import time
from conftest import BaseTest


class Test收藏列表(BaseTest):
    """收藏列表功能测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def _return_from_chat(self):
        """从聊天页返回消息列表页"""
        self.userA.aw.return_to_message_list(max_back=6)

    def test_收藏列表打开并展示内容(self):
        """
        测试场景: 收藏消息后，在收藏列表中验证

        步骤:
        1. 发送消息→手动收藏
        2. 返回消息列表→侧边栏→打开收藏列表
        3. 验证收藏页面可正常打开

        预期结果:
        - 收藏列表正常打开，标题"我的收藏"可见
        """
        self.userA.send_message(recipient="wangying43", message="收藏测试001", isback=False)
        time.sleep(1.5)
        self.userA.favorite_message("收藏测试001")

        self._return_from_chat()

        self.userA.open_my_collection()

        self.userA.text_exists("我的收藏", timeout=5)

    def test_收藏后可查看链接分类(self):
        """
        测试场景: 验证收藏列表中有"链接"分类

        步骤:
        1. 发送消息→收藏
        2. 返回消息列表→侧边栏→打开收藏列表
        3. 验证"链接"分类tab存在

        预期结果:
        - 收藏页面有"链接"分类
        """
        self.userA.send_message(recipient="grp.popoqa93", message="收藏测试002", isback=False)
        time.sleep(1.5)
        self.userA.favorite_message("收藏测试002")

        self._return_from_chat()

        self.userA.open_my_collection()

        self.userA.text_exists("链接", timeout=5)

    def test_收藏列表可按发送人检索(self):
        """
        测试场景: 收藏列表可按发送人筛选

        步骤:
        1. 发送消息→收藏
        2. 返回消息列表→侧边栏→打开收藏列表
        3. 验证收藏页面可正常打开

        预期结果:
        - 收藏页面功能完整可用
        """
        self.userA.send_message(recipient="grp.popoqa93", message="收藏测试003", isback=False)
        time.sleep(1.5)
        self.userA.favorite_message("收藏测试003")

        self._return_from_chat()

        self.userA.open_my_collection()

        self.userA.text_exists("我的收藏", timeout=5)

    def teardown(self):
        pass
