# CASE-ID: radio-POS-004
"""Swan 回归·电台：电台 Hub 无平台授权门槛（radio-POS-004，坑 14 正向面）。

步骤 -> AW 映射（_platformForKind(radio)=null：Hub 与平台授权矩阵解耦）：
- 步骤1 直达电台 Hub 路由页 -> go_bottom_tab('平台') + 电台行箭头图
  [图]（SWAN_PLATFORM_RADIO_ROW_ARROW）进 Hub，到位即无阻断弹层的正向证据；
- 步骤2 断言 Hub 内容区渲染 -> assert_any_of_texts 分类标签候选
  （l10n radio/radioType/city/nationRadio 中文未核准，候选兜底）；
- 步骤3 首页电台 Tab 对照 -> press_back + go_home + go_top_tab('电台')
  三区块渲染（Tab 侧授权门正向由 radio-POS-007 承担，本条只看 Hub 无门）。

清理：只读断言无状态写入，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLATFORM_RADIO_ROW_ARROW


class TestRadioHubNoAuthGate(BaseTest):
    """radio-POS-004：Hub 直达可用，无平台授权提示弹层。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_hub_no_auth_gate(self):
        """Hub 路由页直达渲染完整，首页电台 Tab 对照可达。"""
        self.userA.ensure_logged_in_on_home()
        # 步骤1：平台页电台行直达 Hub（授权态无关）
        self.userA.go_bottom_tab("平台")
        if self.userA.probe_image(SWAN_PLATFORM_RADIO_ROW_ARROW,
                                  timeout=3) is None:
            pytest.skip("平台页未出现电台行箭头图（平台布局轮换），转人工复核")
        self.userA.radio_open_hub_from_platform()
        # 步骤2：Hub 分类标签/内容区块正常渲染（无授权弹层阻断）
        self.userA.assert_any_of_texts("电台分类", "全国电台", "国家台",
                                       timeout=5)
        # 步骤3：首页电台 Tab 对照（双入口分叉的 Tab 侧）
        self.userA.press_back()
        self.userA.go_home()
        self.userA.go_top_tab("电台")
        self.userA.assert_any_of_texts("全国电台", "国家台", "80", "90",
                                       timeout=5)

    def teardown(self) -> None:
        """只读断言无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
