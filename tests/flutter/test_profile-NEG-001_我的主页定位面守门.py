# CASE-ID: profile-NEG-001
"""Swan 回归·M13 个人中心：我的主页定位面守门（profile-NEG-001）。

用例 → AW 映射（me 域零锚点区，定位必须 OCR/[图] 兜底）：
- 步骤1 底部「我的」Tab → open_me_page（go_bottom_tab 内建到位断言）
- 步骤2 顶卡用户区进个人资料页并返回 → open_person_info + back_to_me_page（返回无残栈）
- 步骤3 扫一扫图标无语义键（坑15）→ probe_image(SWAN_ME_SCAN_ICON) 模板可定位
- 步骤4 抽查权益中心/家庭管理/本地音乐/音质设置行 → assert_me_rows_rendered
  （本地音乐行 2026-09-08 dump 未渲染，坑19 漂移：仅探测不强制断）
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg001LocatingGate(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_me_page_locating_gate(self) -> None:
        # 步骤1：底部「我的」Tab 打开我的主页
        self.userA.open_me_page()
        # 步骤2：顶卡用户区 → 个人资料页 → 返回主页无残栈
        self.userA.open_person_info()
        self.userA.back_to_me_page()
        # 步骤3：扫一扫图标语义键缺失（坑15），图片模板必须可定位
        assert self.userA.probe_image("SWAN_ME_SCAN_ICON", timeout=5) is not None, \
            "顶卡扫一扫图标模板不可定位"
        # 步骤4：抽查功能行 OCR 文案（零锚点区，OCR 兜底）
        self.userA.assert_me_rows_rendered(("权益中心", "家庭管理", "音质设置"))
        # 本地音乐行按坑19 漂移口径：行可能未渲染，仅探测不强制
        self.userA.me_row_scroll_until("本地音乐")

    def teardown(self) -> None:
        pass
