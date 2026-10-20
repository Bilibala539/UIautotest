# CASE-ID: home-POS-007
"""Swan 回归·首页：音乐 Tab 平台区块渲染(home-POS-007,部分转换)。

步骤→AW 映射：
- 进音乐 Tab → ensure_logged_in_on_home + go_top_tab('音乐')
- 断言平台分组区块渲染（Catalog 就绪门槛=YAML 要求等待，timeout 放宽承载）
  → text_exists('QQ音乐', timeout=20) + text_exists('网易云音乐', timeout=10)
  （分组标题 [OCR] 为知识库拍板的生效断言）

⚠️ 部分转换注记：YAML 另断言"3 列网格布局、分组顺序、平台数 ≤6"——网格
列数/分组顺序属视觉布局，OCR 无法判定，不做伪断言；数据依赖服务端 Catalog
hasLoaded（timeout 承载等待）。
cleanup：无用例私有清理（冷启动模型）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestMusicTabPlatformBlocks(SwanRP03Mixin, BaseTest):
    """音乐 Tab 渲染平台分组区块（QQ音乐/网易云音乐分组标题可见）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_music_tab_platform_blocks_visible(self):
        """进音乐 Tab，断言平台分组区块标题渲染（Catalog 就绪等待）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('音乐')

        self.userA.text_exists('QQ音乐', timeout=20)
        self.userA.text_exists('网易云音乐', timeout=10)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在音乐 Tab
