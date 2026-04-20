"""
测试用例: 查看设备存储占用图表
探索来源: AI自主探索POPO App生成
探索补全: 原始用例步骤模糊，通过自主探索App补全操作路径
实际路径: 侧边栏→设置→通用→(滚动)存储空间→验证存储信息展示
"""
from conftest import BaseTest
import time


class TestViewStorageUsage(BaseTest):
    """查看设备存储占用图表 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_view_storage_usage(self):
        """
        进入设置→通用→存储空间，验证存储占用信息展示
        """
        # 打开侧边栏→设置
        self.userA.open_sidebar()
        time.sleep(1)
        self.userA.click_text("设置")
        time.sleep(1)

        # 点击通用
        self.userA.click_text("通用")
        time.sleep(1)

        # 向下滚动找到存储空间
        self.userA.aw.swipe_up(300)
        time.sleep(1)

        # 点击存储空间
        self.userA.click_text("存储空间")
        time.sleep(2)

        # 验证存储空间页面展示了存储信息（有"清理"按钮和MB/GB单位）
        clean_pos = self.userA.aw.find_text_by_ocr("清理", timeout=5)
        assert clean_pos is not None, "存储空间页面应有清理按钮"

        mb_pos = self.userA.aw.find_text_by_ocr("MB", timeout=3)
        assert mb_pos is not None, "存储空间页面应显示存储大小(MB)"

    def teardown(self):
        pass
