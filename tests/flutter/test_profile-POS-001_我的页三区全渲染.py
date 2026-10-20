# CASE-ID: profile-POS-001
"""Swan 回归·M13 个人中心：我的页三区全渲染冒烟（profile-POS-001）。

用例 → AW 映射（A- 级全页冒烟）：
- 顶卡：昵称 OCR 读取（me_top_nickname）+ 明文手机号 text_exists(userA.phone)
- 功能行三区全渲染（OCR 文案锚，滚动逐行断言）：
  权益组（权益中心/充值与消费记录）、内容组（家庭管理/SWAN收藏）、
  设备组（设备管理/音质设置）、更多组（帮助与反馈/关于与升级）
- 本地音乐行 2026-09-08 dump 未渲染（坑19 漂移）→ 条件探测不强断
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos001MePageFullRender(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_me_page_full_render(self) -> None:
        self.userA.open_me_page()
        # 顶卡
        self.userA.me_top_nickname()
        self.userA.text_exists(self.userA.phone, timeout=5)
        # 功能行三区全渲染
        self.userA.assert_me_rows_rendered(
            ("权益中心", "充值与消费记录", "家庭管理", "SWAN收藏",
             "设备管理", "音质设置", "帮助与反馈", "关于与升级")
        )
        # 本地音乐行（坑19 漂移）：仅探测记录
        self.userA.me_row_scroll_until("本地音乐")

    def teardown(self) -> None:
        pass
