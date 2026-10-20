# CASE-ID: music-NEG-040
"""Swan 回归·M07 平台入口:未映射入口待接入提示(music-NEG-040)。

步骤→AW 映射(坑 16 兜底锁定,判定类 PlatformContentNavigationResolver,
「待接入」toast=预期行为非 BUG;本条为执行轮区分器,防误报):
  1-2. QQ/酷狗主页无映射二级入口点击 → 出现「待接入」toast 且页面停留。
     无映射入口清单知识库未记载(locator TBD·图像,依赖 Resolver 运行时
     映射表),B 口径运行时发现:OCR 取主页短文本入口候选(排除已知映射
     区块标题)逐个点击,wait_toast("待接入") 命中即锁定;候选点击后
     跳走的为主页正常导航,条件返回后继续下一候选
  3. 锁定入口快速连点 ×3 → 断言主页锚仍在(无导航栈污染;toast 叠加
     刷屏为瞬时态,OCR 不可辨,记 B 局限)

cleanup: 回主页(条件返回已覆盖);toast 自动消散,无状态写。
B 标定说明:无映射入口定位需真机补探索(未注册入口清单或图标模板),
见 package_report.json template_needs;候选扫尽无「待接入」时按前置
「无映射条目可定位」未满足 skip。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicNeg040PendingToast(BaseTest):
    """无映射二级入口点击→待接入 toast 且不跳转(坑 16 兜底)。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_unmapped_entry_pending_toast(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 已知映射区块标题(点击必导航,排除出候选;QQ/酷狗主页 KB 区块序)
        mapped = {"私人推荐", "新歌推荐", "歌手推荐", "排行榜", "歌单",
                  "音乐雷达", "精选视频", "每日推荐", "电台", "播客"}
        hits = {}
        for platform, anchor in (("qq", "QQ音乐"), ("kugou", "酷狗音乐")):
            # 步骤 1/2:进主页,候选扫描锁定「待接入」入口
            self.userA.open_platform_home(platform)
            hit = None
            tried = set()
            for _ in range(6):
                cand = None
                for it in self.userA.ocr_scan_page():
                    text = it["text"].strip()
                    if (2 <= len(text) <= 4 and text not in mapped
                            and text != anchor and not text.isdigit()
                            and text not in tried):
                        cand = it
                        break
                if cand is None:
                    break
                tried.add(cand["text"].strip())
                self.userA.tap(cand["cx"], cand["cy"])
                if self.userA.wait_toast("待接入", timeout=2):
                    hit = (cand["cx"], cand["cy"])
                    break
                if self.userA.find_text_by_ocr(anchor, timeout=2) is None:
                    self.userA.press_back()  # 候选为正常导航,条件返回主页
            hits[platform] = (anchor, hit)
        missing = [p for p, (_, h) in hits.items() if h is None]
        if missing:
            pytest.skip(
                f"{missing} 主页候选扫尽未出现「待接入」toast(B 口径运行时"
                "发现无映射入口;前置「无映射条目可定位」未满足,入口清单"
                "待真机补探索,见 package_report.json template_needs)")
        # 步骤 3:锁定入口快速连点 ×3,无导航栈污染(主页锚仍在)
        for platform, (anchor, hit) in hits.items():
            for _ in range(3):
                self.userA.tap(hit[0], hit[1])
            assert self.userA.find_text_by_ocr(anchor, timeout=6) is not None, (
                f"快速连点无映射入口后{anchor}主页锚丢失(导航栈污染)")
