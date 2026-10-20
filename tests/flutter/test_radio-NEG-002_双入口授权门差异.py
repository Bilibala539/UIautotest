# CASE-ID: radio-NEG-002
"""Swan 回归·电台：双入口授权门差异——Hub 零门槛/首页 Tab 有门（radio-NEG-002，部分转换）。

步骤 -> AW 映射（坑 14：Hub=_platformForKind(radio)=null 与平台授权矩阵
解耦；首页 Tab=ensureHomePlatformAuthorized(terraceType) 授权门；码值
分档为服务端预置面，按坑 9 口径不做文案级码值断言，以入口可达性为
可观察对照）：
- 步骤1 未授权态直路由进电台 Hub -> go_bottom_tab('平台') + 电台行
  箭头图[图]（SWAN_PLATFORM_RADIO_ROW_ARROW）进 Hub，渲染到位且无授权
  弹层（radio_open_hub_from_platform + Hub 区块锚断言）；
- 步骤2/3 同账号进首页电台 Tab 授权门差异面 -> go_top_tab('电台') 授权
  弹层探测（「授权通知」/「去授权」候选，verify-run3 实测弹层在位）：
  未授权态弹层在位即断言差异成立（Hub 无门 vs Tab 有门）；已授权态
  （无弹层）差异不可达 -> pytest.skip 转授权预置（SKIP-AUTH 反口径，
  正向面由 radio-POS-007 承担）；
- 步骤4 全国台入口（码值 0）零门槛对照 -> Hub 内 tap_card_by_texts 进
  全国台页渲染到位（码值 0 入口与授权态无关，与步骤2 Tab 授权门成
  分层对照）。

不可观测面：码值分档矩阵（服务端预置面）与授权门码值校验分支为
服务端/源码面，UI 侧仅断言弹层在位与入口可达对照。
清理：只读断言无状态写入（不点「去授权」——授权态变更入口禁误触），
teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLATFORM_RADIO_ROW_ARROW


class TestRadioDualEntryAuthGateDiff(BaseTest):
    """radio-NEG-002：Hub 零门槛与首页 Tab 授权门差异为设计行为。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_dual_entry_auth_gate_diff(self):
        """Hub 直进无授权弹层；同账号 Tab 授权门在位（差异一致）。"""
        self.userA.ensure_logged_in_on_home()
        # 步骤1：Hub 直路由进电台 Hub（授权态无关，零门槛正向）
        self.userA.go_bottom_tab("平台")
        if self.userA.probe_image(SWAN_PLATFORM_RADIO_ROW_ARROW,
                                  timeout=3) is None:
            pytest.skip("平台页未出现电台行箭头图（平台布局轮换），转人工复核")
        self.userA.radio_open_hub_from_platform()
        # Hub 渲染到位且无授权弹层阻断（零门槛正向证据）
        self.userA.assert_any_of_texts("电台分类", "全国电台", "国家台",
                                       timeout=5)
        # 步骤2/3：同账号首页电台 Tab——授权门差异断言（未授权态守卫）
        self.userA.press_back()
        self.userA.go_home()
        self.userA.go_top_tab("电台")
        gate_visible = (
            self.userA.find_text_by_ocr("授权通知", timeout=3) is not None
            or self.userA.find_text_by_ocr("去授权", timeout=2) is not None)
        if not gate_visible:
            pytest.skip("当前账号平台授权态非未授权形态（Tab 无授权门弹层），"
                        "未授权/最小授权态需人工预置——双入口差异断言不可达")
        # 差异一致性：步骤1 Hub 无门直进 vs 本步骤 Tab 授权门在位
        self.userA.assert_any_of_texts("授权通知", "去授权", timeout=2)
        # 步骤4：全国台入口（码值 0）零门槛对照——Hub 侧直进全国台页
        self.userA.press_back()
        self.userA.go_home()
        self.userA.go_bottom_tab("平台")
        self.userA.radio_open_hub_from_platform()
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)

    def teardown(self) -> None:
        """只读断言无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
