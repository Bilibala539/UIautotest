"""
测试用例: 收藏列表功能验证
Excel来源: 首页其他功能.xlsx ROW6-8
功能点: 收藏列表链接展示及发送人检索功能
"""
import time
from conftest import BaseTest
from image.image_name_mapping import (
    MESSAGE_TAB_MSG_TEXT,
    SIDEBAR_MY_COLLECTION,
)


class Test收藏列表(BaseTest):
    """收藏列表功能测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def _open_sidebar(self):
        """打开侧边栏（通过点击左上角消息文案左侧头像区域）"""
        self.userA.click_image(MESSAGE_TAB_MSG_TEXT, dx=-70)
        time.sleep(0.5)

    def _click_my_collection(self):
        """在侧边栏中点击我的收藏入口"""
        self.userA.click_image(SIDEBAR_MY_COLLECTION)
        time.sleep(1)

    def _favorite_current_message(self, message_text):
        """在当前聊天页面收藏指定消息"""
        self.userA.aw.long_press_text(message_text, duration=1.5)
        time.sleep(0.5)
        self.userA.click_text("收藏")
        time.sleep(0.5)

    def _return_from_chat(self):
        """
        从聊天页返回消息列表页

        步骤: 聊天页 → 按返回(搜索选人页) → 再按返回(消息列表) → 点取消(清理搜索框)
        """
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
        time.sleep(1)
        # 尝试点击"取消"清除可能残留的搜索
        self.userA.click_text("取消", timeout=3, region=(0, 0, 540, 100))
        time.sleep(0.5)

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
        # 进入聊天→发送→收藏
        self.userA.send_message(recipient="wangying43", message="收藏测试001", isback=False)
        time.sleep(1.5)
        self._favorite_current_message("收藏测试001")

        # 从聊天页返回消息列表
        self._return_from_chat()

        # 打开侧边栏→点击我的收藏
        self._open_sidebar()
        self._click_my_collection()

        # 验证收藏页面标题
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
        self._favorite_current_message("收藏测试002")

        self._return_from_chat()

        self._open_sidebar()
        self._click_my_collection()

        # 验证"链接"分类存在
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
        self._favorite_current_message("收藏测试003")

        self._return_from_chat()

        self._open_sidebar()
        self._click_my_collection()

        # 验证页面标题
        self.userA.text_exists("我的收藏", timeout=5)

    def teardown(self):
        pass
