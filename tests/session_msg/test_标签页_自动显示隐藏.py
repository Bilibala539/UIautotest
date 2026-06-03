"""
测试用例: 标签页优化（3期）- 展示区域标签页自动显示与隐藏
Excel来源: 会话区及消息.xlsx 行 30(云文档tab), 31(链接tab), 32(pin tab), 33(文件tab)
"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestTabAutoShowHide(BaseTest):
    """标签页自动显示与隐藏功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_cloud_doc_tab_auto_show(self):
        """
        测试场景: 发送云文档消息后云文档tab自动显示
        操作: 在任意会话中发送一条云文档消息
        预期: 云文档标签页tab自动显示在展示区域

        Excel行号: 30 (index 0-based)
        """
        import time
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)

        # 发送一条包含云文档链接的消息
        self.userA.aw.click_image("CHAT_INPUT_BOX", region="HALF_DOWN")
        self.userA.aw.input_text("https://docs.popo.netease.com/lingxi/test_auto")
        self.userA.aw.click_image("CHAT_SEND_BUTTON", region="HALF_DOWN")
        time.sleep(2)

        # 进入标签页查看
        self.userA.aw.click_text("设置", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

        # 验证云文档tab显示
        self.userA.aw.text_exists("云文档", timeout=5)

    def test_link_tab_auto_show(self):
        """
        测试场景: 发送链接消息后链接tab自动显示
        操作: 在任意会话中发送一条链接消息
        预期: 链接标签页tab自动显示在展示区域

        Excel行号: 31 (index 0-based)
        """
        import time
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)

        # 发送链接消息
        self.userA.aw.click_image("CHAT_INPUT_BOX", region="HALF_DOWN")
        self.userA.aw.input_text("https://www.163.com")
        self.userA.aw.click_image("CHAT_SEND_BUTTON", region="HALF_DOWN")
        time.sleep(2)

        # 进入标签页
        self.userA.aw.click_text("设置", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

        # 验证链接tab显示
        self.userA.aw.text_exists("链接", timeout=5)

    def test_pin_tab_auto_show(self):
        """
        测试场景: 对消息进行pin操作后pin tab自动显示
        操作: 在任意会话中对一条消息进行pin操作
        预期: pin标签页tab自动显示在展示区域

        Excel行号: 32 (index 0-based)
        """
        import time
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)

        # 先发送一条消息
        self.userA.aw.click_image("CHAT_INPUT_BOX", region="HALF_DOWN")
        self.userA.aw.input_text("pin测试消息")
        self.userA.aw.click_image("CHAT_SEND_BUTTON", region="HALF_DOWN")
        time.sleep(1)

        # pin这条消息
        self.userA.aw.pin_message("pin测试消息")
        time.sleep(1)

        # 进入标签页验证
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.click_text("设置", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

        # 验证Pin tab显示
        self.userA.aw.text_exists("Pin", timeout=5)

    def test_file_tab_auto_show(self):
        """
        测试场景: 发送文件消息后文件tab自动显示
        操作: 在任意会话中发送一条文件消息
        预期: 文件标签页tab自动显示在展示区域

        Excel行号: 33 (index 0-based)
        """
        import time
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)

        # 发送文件（通过+面板）
        self.userA.aw.click_image("CHAT_PLUS_BUTTON", region="HALF_DOWN")
        time.sleep(1)
        self.userA.aw.click_text("文件", timeout=5, dy=10)
        time.sleep(2)

        # 选择第一个文件并发送
        self.userA.aw.click_text("发送", timeout=10)
        time.sleep(2)

        # 进入标签页验证
        self.userA.aw.click_text("设置", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

        # 验证文件tab显示
        self.userA.aw.text_exists("文件", timeout=5)

    def teardown(self):
        self.userA.aw.go_to_home()
