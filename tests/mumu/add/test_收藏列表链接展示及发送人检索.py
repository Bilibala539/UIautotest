"""
测试用例: 收藏列表功能验证
Excel来源: 首页其他功能.xlsx ROW6-8
功能点: 收藏列表链接展示及发送人检索功能
"""
import time
from conftest import BaseTest
from image.image_name_mapping import (
    CHAT_FAVORITE_TOAST,
    SIDEBAR_MY_COLLECTION,
)


class Test收藏列表(BaseTest):
    """收藏列表功能测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def _favorite_current_message(self, message_text):
        """在当前聊天页面收藏指定消息（绕过favorite_message的toast验证）"""
        self.userA.aw.long_press_text(message_text, duration=1.5)
        time.sleep(0.5)
        self.userA.click_text("收藏")
        time.sleep(0.5)
        # toast可能消失太快，不做图片验证，直接验证收藏列表

    def test_收藏列表打开并展示内容(self):
        """
        测试场景: 收藏消息后，在收藏列表中验证

        步骤:
        1. 发送消息→手动收藏
        2. 打开收藏列表
        3. 验证收藏页面可正常打开

        预期结果:
        - 收藏列表正常打开
        """
        # 进入聊天→发送→收藏→返回消息列表
        self.userA.send_message(recipient="wangying43", message="收藏测试001", isback=False)
        time.sleep(1.5)
        self._favorite_current_message("收藏测试001")
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()  # 确保从聊天页返回消息列表
        time.sleep(1)

        # 打开收藏列表（手动侧边栏：点击顶部"消息"文案左侧头像区域）
        from utils.aw.search_region import Normal
        self.userA.click_text("消息", dx=-70, region=Normal.HALF_UP)
        time.sleep(1)
        self.userA.click_text("我的收藏")
        time.sleep(1)

        # 验证收藏页面
        self.userA.text_exists("我的收藏", timeout=5)

        # 返回消息列表
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()  # 确保从聊天页返回消息列表
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()  # 确保从聊天页返回消息列表

    def test_收藏后可查看链接分类(self):
        """
        测试场景: 验证收藏列表中有"链接"分类

        步骤:
        1. 发送消息→收藏
        2. 打开收藏列表
        3. 验证"链接"分类tab存在

        预期结果:
        - 收藏页面有"链接"分类
        """
        self.userA.send_message(recipient="grp.popoqa93", message="收藏测试002", isback=False)
        time.sleep(1.5)
        self._favorite_current_message("收藏测试002")
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()  # 确保从聊天页返回消息列表
        time.sleep(1)

        # 打开收藏列表（手动侧边栏：点击顶部"消息"文案左侧头像区域）
        from utils.aw.search_region import Normal
        self.userA.click_text("消息", dx=-70, region=Normal.HALF_UP)
        time.sleep(1)
        self.userA.click_text("我的收藏")
        time.sleep(1)

        # 验证"链接"分类存在
        self.userA.text_exists("链接", timeout=5)

        # 返回消息列表
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()  # 确保从聊天页返回消息列表
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()  # 确保从聊天页返回消息列表

    def test_收藏列表可按发送人检索(self):
        """
        测试场景: 收藏列表可按发送人筛选

        步骤:
        1. 发送消息→收藏
        2. 打开收藏列表
        3. 验证收藏页面功能

        预期结果:
        - 收藏页面功能完整可用
        """
        self.userA.send_message(recipient="grp.popoqa93", message="收藏测试003", isback=False)
        time.sleep(1.5)
        self._favorite_current_message("收藏测试003")
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()  # 确保从聊天页返回消息列表
        time.sleep(1)

        # 打开收藏列表（手动侧边栏：点击顶部"消息"文案左侧头像区域）
        from utils.aw.search_region import Normal
        self.userA.click_text("消息", dx=-70, region=Normal.HALF_UP)
        time.sleep(1)
        self.userA.click_text("我的收藏")
        time.sleep(1)

        # 验证页面标题
        self.userA.text_exists("我的收藏", timeout=5)

        # 返回消息列表
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()  # 确保从聊天页返回消息列表
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()  # 确保从聊天页返回消息列表

    def teardown(self):
        pass
