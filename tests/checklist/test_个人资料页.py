"""
测试用例: 个人资料页
Excel来源: 首页其他功能.xlsx ROW19-20
功能点: 个人资料页
"""
from conftest import BaseTest


class Test个人资料页(BaseTest):
    """个人资料页测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_有签名展示个人信息(self):
        """
        测试场景: 查看个人资料，验证有签名时展示完整信息

        步骤:
        1. 打开侧边栏，进入个人资料页
        2. OCR采集个人信息
        3. 验证签名、账号、电话等关键字段存在

        预期结果:
        - 成功进入个人资料页
        - 能采集到签名（如有）、账号等关键信息
        """
        profile = self.userA.view_my_profile()

        # 验证关键字段存在
        assert "account" in profile, "未采集到账号信息"
        # 验证至少采集到3个以上字段（确保页面展示正常）
        assert len(profile) >= 3, f"采集到的字段太少: {profile}"

    def test_分享icon进入推荐页面(self):
        """
        测试场景: 个人资料页点击品牌/二维码icon进入"我的二维码"页

        新版UI: 旧"分享"按钮已移除，右上角改为品牌/二维码图标(OCR识别为"品")，
        点击后进入"我的二维码"页面，底部有"发送给同事或群组"按钮。

        步骤:
        1. 打开侧边栏→点击用户名区域进入个人资料页
        2. 验证个人资料页加载（个性签名可见）
        3. 点击右上角品牌/二维码图标("品")
        4. 验证进入"我的二维码"页（"发送给同事或群组"可见）
        5. 返回消息列表
        """
        from image.image_name_mapping import SIDEBAR_MY_COLLECTION
        import time

        # 打开侧边栏→点击用户头像区域进入个人资料页
        self.userA.open_sidebar()
        self.userA.click_image(SIDEBAR_MY_COLLECTION, dy=-180)
        time.sleep(1)

        # 验证进入个人资料页（应展示用户信息）
        self.userA.text_exists("个性签名", timeout=5)

        # 点击右上角品牌/二维码图标（OCR识别为"品"）
        self.userA.click_text("品")
        time.sleep(1)

        # 验证进入"我的二维码"页面
        self.userA.text_exists("发送给同事或群组", timeout=5)

        # 返回消息列表（从我的二维码页→个人资料页→消息列表）
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
        time.sleep(0.5)

    def teardown(self):
        pass
