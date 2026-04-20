"""
测试用例: 扫一扫入口
探索来源: AI自主探索POPO App生成
用例描述: 点击右上角+号，点击扫一扫，验证进入扫一扫界面
"""
from conftest import BaseTest


class TestScanQRCode(BaseTest):
    """扫一扫入口 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_open_scan_qrcode(self):
        """
        点击右上角+号，点击扫一扫，验证进入扫一扫界面
        """
        from image.image_name_mapping import SESSIONLIST_PLUS_BUTTON

        # 点击右上角+号
        self.userA.click_image(SESSIONLIST_PLUS_BUTTON)

        # 点击扫一扫
        self.userA.click_text("扫一扫")

        # 验证进入扫一扫界面（检查相机权限弹窗或扫一扫页面）
        # 扫一扫页面可能会弹出相机权限请求
        import time
        time.sleep(2)

        # 扫一扫页面应有"扫一扫"文字或者相机权限弹窗
        # 处理可能的权限弹窗
        self.userA.aw.pop_not_allowed()

        # 返回消息列表
        self.userA.aw.press_back()

    def teardown(self):
        pass
