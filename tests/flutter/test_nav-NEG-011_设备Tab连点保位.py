# CASE-ID: nav-NEG-011
"""Swan 回归·M03 主框架导航：设备 Tab 同页连点 5 次保持列表位（nav-NEG-011）。

用例 → AW 映射：
- 登录态首页壳 → ensure_logged_in_on_home()；切设备页 → go_bottom_tab("设备")
- 列表下移一屏 → scroll_down()
- 采样内容区锚点行 → ocr_scan_page() 取 cy∈(200,1200)、长度≥2 且非纯
  数字的文本行（避开导航栏/播放条带与页码类噪声），取中位行文案
- 连点 5 次 Tab → reclick_bottom_tab_label("设备", 5)（导航标签 [OCR]
  定位——选中态无未选中态模板）
- 浏览位置保持 → text_exists(锚点) 断言
注：设备列表不足一屏时锚点为首屏行，断言退化为平凡真（口径见 notes）。
清理：无（导航壳操作无副作用，冷启动模型自然复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestNavNeg011ReclickKeepsScroll(SwanRP01Mixin, BaseTest):
    """设备 Tab 同页连点 5 次保持列表位（nav-NEG-011）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_reclick_device_tab_keeps_position(self):
        """连点设备 Tab 5 次，滚动后的列表位置应保持不变。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("设备")
        self.userA.scroll_down()
        items = [i for i in self.userA.ocr_scan_page()
                 if 200 < i.get("cy", 0) < 1200
                 and len((i.get("text") or "").strip()) >= 2
                 and not (i.get("text") or "").strip().isdigit()]
        assert items, "设备页内容区无可用锚点文本（页面空/OCR 失效）"
        anchor = items[len(items) // 2]["text"].strip()
        self.userA.reclick_bottom_tab_label("设备", 5)
        self.userA.text_exists(anchor, timeout=5)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
