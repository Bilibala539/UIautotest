"""
测试用例: 组织架构
Excel来源: 首页其他功能.xlsx ROW32-34
功能点: 组织架构
"""
import time
from conftest import BaseTest


class Test组织架构(BaseTest):
    """组织架构测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_全局搜索组织成员(self):
        """
        测试场景: 在搜索中搜索组织架构内的成员，验证可搜索到

        步骤:
        1. 点击搜索按钮进入搜索页
        2. 切换到联系人Tab
        3. 搜索组织架构内的成员（如"王英"）
        4. 验证搜索结果中显示该成员

        预期结果:
        - 搜索结果中显示被搜索的组织成员
        """
        # 搜索联系人"王英"（组织架构内成员）
        self.userA.search(tab="联系人", text="王英", isclose=False)

        # 验证搜索结果存在
        from image.image_name_mapping import SEARCH_WANGYING_BLUE, SEARCH_WANGYING_HEAD
        self.userA.image_exists(SEARCH_WANGYING_BLUE)
        self.userA.image_exists(SEARCH_WANGYING_HEAD)
        self.userA.text_exists("效率工程部", region=None)

        # 关闭搜索
        from image.image_name_mapping import SEARCH_CANCEL
        self.userA.click_image(SEARCH_CANCEL)

    def test_组织架构层级显示(self):
        """
        测试场景: 进入通讯录查看组织架构，验证层级显示正常

        步骤:
        1. 点击底部导航栏"通讯录"
        2. 查看组织架构层级
        3. 验证层级内容展示正常

        预期结果:
        - 能正常进入通讯录页面
        - 组织架构层级显示正常
        """
        # 点击底部导航栏"通讯录"
        self.userA.click_text("通讯录")
        time.sleep(2)

        # 验证通讯录页面展示
        from image.image_name_mapping import CONTACTS_TITLE_TEXT
        self.userA.image_exists(CONTACTS_TITLE_TEXT)

        # 验证组织架构入口存在
        self.userA.text_exists("组织架构", timeout=5)

        # 点击进入组织架构
        self.userA.click_text("组织架构")
        time.sleep(1)

        # 验证组织架构页面有内容展示
        self.userA.text_exists("我", timeout=5)

        # 返回消息列表
        self.userA.aw.press_back()
        self.userA.click_text("消息")

    def test_组织架构内好友会话(self):
        """
        测试场景: 与组织架构内的好友进行文字交流

        步骤:
        1. 搜索组织架构内的联系人
        2. 进入会话页面
        3. 发送文字消息
        4. 验证消息发送成功

        预期结果:
        - 能正常与组织架构内好友交流
        - 消息发送成功
        """
        # 发送消息（send_message内含搜人→进会话→输入→发送全流程）
        self.userA.send_message(recipient="wangying43", message="组织架构测试消息", isback=True)

    def teardown(self):
        pass
