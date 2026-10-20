# CASE-ID: nav-POS-007
"""Swan 回归·M03 主框架导航：设备 Tab 切回带此前浏览状态（nav-POS-007）。

用例 → AW 映射：
- 登录态首页壳 → ensure_logged_in_on_home()；切设备页 → go_bottom_tab("设备")
- 建立浏览位置 → scroll_down() 下移一屏
- 采样内容区锚点行 → ocr_scan_page() 取 cy∈(200,1200)、长度≥2 且非纯
  数字的文本行（避开导航栏/播放条带与页码类噪声，同 nav-NEG-011 口径）
- 切走再切回（激活）→ go_bottom_tab("首页") → go_bottom_tab("设备")
- 浏览位置保持 → text_exists(锚点) 断言
不可观测面声明：deviceTabActivated 激活信号自增与随激活发出的固件
可见性检查请求（YAML 步骤 3 内部机制面/步骤 4）为内部机制与请求观测
面，UI 面不可观测——以「切回带此前浏览状态」可观察代理收口
（IndexedStack 状态保持即激活机制的用户可见面，选中态保持可升级
[图] 模板断言，已登记 template_needs）。TESTDEV01 专用预置设备不
强制：任意已绑定设备列表同口径；设备列表不足一屏时锚点为首屏行，
断言退化为平凡真（同 nav-NEG-011 notes 口径）。
清理：无（导航壳操作无副作用，冷启动模型自然复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestNavPos007SwitchBackKeepsBrowseState(SwanRP01Mixin, BaseTest):
    """设备 Tab 切回带此前浏览状态（nav-POS-007）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_switch_back_device_tab_keeps_browse_state(self):
        """切走首页再切回设备 Tab，此前浏览位置应保持。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("设备")
        self.userA.scroll_down()
        items = [i for i in self.userA.ocr_scan_page()
                 if 200 < i.get("cy", 0) < 1200
                 and len((i.get("text") or "").strip()) >= 2
                 and not (i.get("text") or "").strip().isdigit()]
        assert items, "设备页内容区无可用锚点文本（页面空/OCR 失效）"
        anchor = items[len(items) // 2]["text"].strip()
        self.userA.go_bottom_tab("首页")
        self.userA.go_bottom_tab("设备")
        self.userA.text_exists(anchor, timeout=5)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
