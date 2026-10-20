# CASE-ID: home-NEG-001
"""Swan 回归·首页：重登后顶 Tab 从推荐开始(home-NEG-001)。

步骤→AW 映射：
- 进入首页并停留电台 Tab → ensure_logged_in_on_home + go_top_tab('电台')
  （go_top_tab 内含顶 Tab 选中态锚断言，确认切 Tab 生效）
- 退出登录 → logout_if_needed（登出并断言落登录页）
- 重新登录 → login_with_password(phone, password)（账号走 .env.local 注入）
- 断言回到首页且顶 Tab 从"推荐"开始（不恢复上次停留）→ assert_on_home
  + 推荐 Tab 选中态 [图] SWAN_HOME_TAB_RECOMMEND_SEL 探测

cleanup：无用例私有清理（冷启动模型，teardown body 一律 pass）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_TAB_RECOMMEND_SEL
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestReLoginTopTabRecommend(SwanRP03Mixin, BaseTest):
    """重登后顶 Tab 从推荐开始，不恢复上次停留的电台 Tab。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_relogin_lands_on_recommend_tab(self):
        """先切到电台 Tab，登出重登后断言顶 Tab 从推荐开始。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('电台')

        self.userA.logout_if_needed()
        self.userA.assert_on_login_page()
        self.userA.login_with_password(self.userA.phone, self.userA.password)
        self.userA.assert_on_home()

        # 断言：顶 Tab 从推荐开始（推荐 Tab 选中态 [图] 可见，而非恢复电台）
        assert self.userA.find_image(SWAN_HOME_TAB_RECOMMEND_SEL, timeout=10) is not None, (
            "重登后推荐 Tab 选中态 [图] 未命中——顶 Tab 可能恢复了上次停留的电台 Tab")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在首页，顶 Tab 在推荐
