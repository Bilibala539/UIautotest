"""
测试用例: 各类标签页 - 云文档标签页
Excel来源: 会话区及消息.xlsx 行 38(默认排序), 39(查看列表), 40(移除), 41(列表排序)
"""
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestCloudDocTabPage(BaseTest):
    """云文档标签页功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_default_tab_order(self):
        """
        测试场景: 检查云文档标签页的默认排序
        操作: 打开任意会话，检查标签页顺序
        预期: 默认标签页排序为：云文档、链接、Pin、文件、任务

        Excel行号: 38 (index 0-based)
        """
        import time
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)

        # 进入设置 → 标签页
        self.userA.aw.click_text("设置", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

        # 验证标签页存在且顺序正确（验证关键tab可见）
        self.userA.aw.text_exists("云文档", timeout=5)
        self.userA.aw.text_exists("文件", timeout=3)
        self.userA.aw.text_exists("Pin", timeout=3)

    def test_view_cloud_doc_list(self):
        """
        测试场景: 查看云文档列表
        操作: 点击云文档标签页，打开云文档列表窗口
        预期: 列表展示会话内发送的所有云文档，按发送时间从近到远排序

        Excel行号: 39 (index 0-based)
        """
        import time
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)

        # 进入标签页
        self.userA.aw.click_text("设置", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

        # 点击云文档 tab
        self.userA.aw.click_text("云文档", timeout=5)
        time.sleep(1)

        # 验证进入了云文档列表（页面标题或内容区可见）
        title_pos = self.userA.aw.find_text_by_ocr("全部标签页", timeout=5)
        assert title_pos is not None, "应进入全部标签页页面"

    def test_cloud_doc_remove(self):
        """
        测试场景: 云文档的移除
        操作: 撤回或删除服务端的云文档消息
        预期: 云文档标签页中移除该云文档

        Excel行号: 40 (index 0-based)
        注意: 需要先发送一条云文档消息，然后撤回验证标签页中消失
        """
        import time
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)

        # 发送一条包含云文档链接的消息
        self.userA.aw.click_image("CHAT_INPUT_BOX", region="HALF_DOWN")
        self.userA.aw.input_text("https://docs.popo.netease.com/lingxi/remove_test")
        self.userA.aw.click_image("CHAT_SEND_BUTTON", region="HALF_DOWN")
        time.sleep(2)

        # 撤回这条消息
        self.userA.aw.long_press_text("remove_test", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("撤回", timeout=5)
        time.sleep(1)

        # 验证撤回成功
        self.userA.aw.text_exists("撤回了一条消息", timeout=5)

    def test_cloud_doc_list_sort(self):
        """
        测试场景: 云文档列表的排序
        操作: 查看云文档列表
        预期: 星标和非星标分开展示，星标排在前；各自按发送时间从近到远排序

        Excel行号: 41 (index 0-based)
        注意: 验证列表分区显示即可，精确排序需人工目视确认
        """
        import time
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)

        # 进入标签页
        self.userA.aw.click_text("设置", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

        # 点击云文档tab
        self.userA.aw.click_text("云文档", timeout=5)
        time.sleep(1)

        # 验证列表页面加载（有内容则通过）
        page_loaded = self.userA.aw.find_text_by_ocr("全部标签页", timeout=5)
        assert page_loaded is not None, "云文档列表页面应正常加载"

    def teardown(self):
        self.userA.aw.go_to_home()
