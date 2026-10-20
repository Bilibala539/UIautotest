# CASE-ID: home-POS-011
"""Swan 回归·首页：电台 Tab 三区块渲染(home-POS-011,部分转换)。

步骤→AW 映射：
- 进电台 Tab → ensure_logged_in_on_home + go_top_tab('电台')
- 断言区块一"全国电台"渲染（数据就绪等待）→ text_exists('全国电台',
  timeout=15)
- 滚动探区块二/三（80/90 年代电台）→ swipe_up() + assert_any_text(
  ['80', '90'], timeout=8)（任一命中即区块渲染证据）

⚠️ 部分转换注记：电台 Tab 详情页（区块点入后的电台列表/详情）知识库标记
未探索（授权门禁拦截未进入），本条只断言三区块在 Tab 壳层渲染，不深入
区块内页（对应 home-POS-008/009/023 搜索域电台详情用例已 skip）。
cleanup：无用例私有清理（冷启动模型）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestRadioTabBlocks(SwanRP03Mixin, BaseTest):
    """电台 Tab 渲染全国电台/80/90 年代电台三区块。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_radio_tab_blocks_visible(self):
        """进电台 Tab，断言全国电台区块与 80/90 年代区块渲染。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('电台')

        self.userA.text_exists('全国电台', timeout=15)
        self.userA.swipe_up()
        matched = self.userA.assert_any_text(['80', '90'], timeout=8)
        assert matched, "翻屏后未 OCR 到 80/90 年代电台区块"

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在电台 Tab
