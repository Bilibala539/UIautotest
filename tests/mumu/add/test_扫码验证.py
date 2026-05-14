"""
测试用例: 扫码验证
Excel来源: 首页其他功能.xlsx ROW27-30
功能点: 扫码验证
"""
import time
from conftest import BaseTest
from image.image_name_mapping import SESSIONLIST_PLUS_BUTTON, SEARCH_CANCEL


class Test扫码验证(BaseTest):
    """扫码验证测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_我的二维码页面(self):
        """
        测试场景: 从扫一扫入口点击"我的二维码"进入我的二维码页面

        步骤:
        1. 点击右上角+号→扫一扫，进入扫码框
        2. 点击下方"我的二维码"
        3. 验证进入我的二维码页面

        预期结果:
        - 成功进入扫码框
        - 点击后跳转到我的二维码页面
        """
        # 点击右上角+号
        self.userA.click_image(SESSIONLIST_PLUS_BUTTON)

        # 点击扫一扫
        self.userA.click_text("扫一扫")
        time.sleep(2)

        # 处理可能的相机权限弹窗
        self.userA.aw.pop_not_allowed()

        # 点击下方"我的二维码"
        self.userA.click_text("我的二维码")
        time.sleep(1)

        # 验证进入我的二维码页面
        self.userA.text_exists("我的二维码", timeout=5)

        # 返回消息列表
        self.userA.aw.press_back()
        self.userA.aw.press_back()

    def test_相册二维码图片不清晰(self):
        """
        测试场景: 从相册选择不清晰的二维码图片，验证弹出错误提示

        步骤:
        1. 进入扫一扫页面
        2. 从相册选择一张不清晰的二维码图片
        3. 验证弹出"错误的二维码"toast

        预期结果:
        - 弹出toast提示"错误的二维码"
        """
        # 点击右上角+号→扫一扫
        self.userA.click_image(SESSIONLIST_PLUS_BUTTON)
        self.userA.click_text("扫一扫")
        time.sleep(2)

        # 处理可能的相机权限弹窗
        self.userA.aw.pop_not_allowed()

        # 点击相册入口（从相册选择二维码图片）
        self.userA.click_text("相册")
        time.sleep(1)

        # 选择一张图片（点击第一张图片）
        self.userA.tap(70, 200)
        time.sleep(1)

        # 验证弹出错误提示
        self.userA.text_exists("错误的二维码", timeout=5)

        # 返回
        self.userA.aw.press_back()
        self.userA.aw.press_back()

    def teardown(self):
        pass
