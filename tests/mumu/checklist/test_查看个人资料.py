"""
测试用例: 查看个人资料

探索来源: AI自主探索POPO App生成
探索记录: explorer_output/screenshots/step7~step9
"""
from conftest import BaseTest


class TestViewMyProfile(BaseTest):
    """查看个人资料测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")

    def test_view_my_profile(self):
        """
        测试场景: 查看个人资料信息

        步骤:
        1. 点击左上角头像区域打开侧边栏
        2. 点击用户名进入个人资料页
        3. OCR采集个人信息（中文昵称、英文昵称、日文昵称、账号、手机号等）
        4. 向上滑动查看更多（岗位名称、组织架构、办公位置）
        5. 验证关键字段不为空
        6. 返回消息列表

        预期结果:
        - 成功打开侧边栏
        - 成功进入个人资料页
        - 能采集到中文昵称、账号等关键信息
        """
        profile = self.userA.view_my_profile()

        # 验证关键字段已采集到
        assert "nickname_cn" in profile, "未采集到中文昵称"
        assert "account" in profile, "未采集到账号"
        assert len(profile) >= 3, f"采集到的字段太少: {profile}"

    def teardown(self):
        pass
