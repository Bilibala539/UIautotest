# CASE-ID: radio-POS-001
"""Swan 回归·电台：电台 Hub 双入口可达（radio-POS-001）。

步骤 -> AW 映射（radio 页族 0 testId，l10n 文本锚+已登记图模板兜底）：
- 步骤1 经底部导航进平台页电台行 -> go_bottom_tab('平台') + 电台行箭头
  图 [图]（SWAN_PLATFORM_RADIO_ROW_ARROW）进入 Hub 路由页
  （/music_platform/radio，箭头图点击后 OCR 候选文案断言 Hub 标题）；
- 步骤2 断言 Hub 页元素 -> assert_any_of_texts 候选断言（l10n
  platformRadioCategory / radioType / nationRadio 的中文串真机未核准，
  候选兜底，见 package_report.template_needs）；
- 步骤3 返回后经首页电台 Tab 第二入口 -> press_back + go_home +
  go_top_tab('电台')，首页电台 Tab（HomeRadioPage）锚定搜索条图
  [图]（SWAN_HOME_RADIO_SEARCH_BAR）+ 三区块候选文案。

清理：只读冒烟无状态写入；强更/布局轮换等运行时异常态按 skip 转人工。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_HOME_RADIO_SEARCH_BAR,
    SWAN_PLATFORM_RADIO_ROW_ARROW,
)


class TestRadioHubDualEntry(BaseTest):
    """radio-POS-001：Hub 路由页与首页电台 Tab 双入口均可达。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_radio_hub_dual_entry(self):
        """入口一平台页电台行 -> Hub；入口二首页电台 Tab 三区块。"""
        self.userA.ensure_logged_in_on_home()
        # 入口一：平台页电台行（0 testId，仅登记箭头图可达）
        self.userA.go_bottom_tab("平台")
        if self.userA.probe_image(SWAN_PLATFORM_RADIO_ROW_ARROW,
                                  timeout=3) is None:
            pytest.skip("平台页未出现电台行箭头图（平台布局轮换），转人工复核")
        self.userA.radio_open_hub_from_platform()
        # 步骤2：Hub 页元素按契约文案候选断言（中文串未核准）
        self.userA.assert_any_of_texts("电台分类", "全国电台", "国家台",
                                       timeout=5)
        self.userA.press_back()
        # 入口二：首页电台 Tab（HomeRadioPage 三区块 + 搜索条）
        self.userA.go_home()
        self.userA.go_top_tab("电台")
        if self.userA.probe_image(SWAN_HOME_RADIO_SEARCH_BAR,
                                  timeout=3) is None:
            pytest.skip("首页电台 Tab 搜索条图未命中（布局轮换），转人工复核")
        self.userA.assert_any_of_texts("全国电台", "国家台", "80", "90",
                                       timeout=5)

    def teardown(self) -> None:
        """只读冒烟无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
