"""
测试用例: 个人资料页 - 点击我的二维码
Excel来源: 首页其他功能.xlsx ROW24
功能点: 个人资料页
探索来源: explorer_output/knowledge/pages/profile_page.md
"""
import time
from conftest import BaseTest


class Test个人资料页二维码(BaseTest):
    """个人资料页二维码测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def _enter_profile_page(self):
        """进入个人资料页"""
        self.userA.open_sidebar()
        time.sleep(1.5)
        self.userA.click_text("吴彦祖>")
        time.sleep(1)
        self.userA.text_exists("个性签名", timeout=5)

    def test_点击我的二维码(self):
        """
        测试场景: 在资料页点击右上角二维码图标进入二维码页面

        步骤:
        1. 侧边栏→点击用户名进入资料页
        2. 点击右上角二维码图标(OCR识别为"品"@485,90)
        3. 验证进入我的二维码页面

        预期结果:
        - 进入我的二维码页面，显示"我的二维码"标题

        备注: ROW22(更改手机号)和ROW23(更改个性签名)无法自动化
        - profile_page.md确认：资料页无"编辑"按钮，字段直接点击在当前版本不可用
        - ROW25(点击我的个人主页)在QR页面中不存在，需进一步探索编辑页入口
        """
        self._enter_profile_page()
        time.sleep(1)

        # 点击右上角二维码图标（OCR误读为"品"但位置正确）
        self.userA.click_text("品")
        time.sleep(1)

        # 验证进入我的二维码页面
        self.userA.text_exists("我的二维码", timeout=5)

        # 返回消息列表
        self.userA.aw.press_back()
        self.userA.aw.press_back()
        self.userA.aw.press_back()

    def teardown(self):
        pass
