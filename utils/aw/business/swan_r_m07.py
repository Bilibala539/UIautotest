"""M07 音乐平台聚合 包级业务 mixin(tcbatch L07 批次新增,2026-10-20)。

纯 mixin 类不继承,由集成方统一挂入 SwanBusiness MRO 后 userA 可直调。
定位口径:[OCR] 文本优先;平台行右侧 [+] 授权钮为图标(知识库实测 OCR 误读
为 +/?),tap_platform_row_plus 走 [图] 模板(可选入参)→ 行带 OCR 字形 →
断言失败(留模板标定提示)三段链;各行 [+] 模板真机补截后回填 template
实参即可,需求登记见 package_report.json template_needs。
行带几何计算仅为 OCR 项聚合(元素锚定),全程无屏幕绝对坐标。
"""
from __future__ import annotations

import time

import pytest


class SwanRM07Mixin:
    """M07 平台授权/平台主页/平台内容页族共用编排。"""

    # 平台代码 -> 平台页·音乐分类行 OCR 文案(knowledge/swan/pages/swan_平台页.md)
    _M07_ROW_TEXTS = {
        "qq": "QQ音乐",
        "netease": "网易云音乐",
        "kugou": "酷狗音乐",
        "spotify": "Spotify",
        "apple": "Apple Music",
        "qobuz": "Qobuz",
    }

    # ------------------------------------------------------------------
    # 内部小工具(下划线私有,用例不得直调)
    # ------------------------------------------------------------------

    @classmethod
    def _m07_row_text(cls, platform: str) -> str:
        """平台代码/别名 -> 平台页行 OCR 文案(未知值原样返回)。"""
        return cls._M07_ROW_TEXTS.get(platform, platform)

    @staticmethod
    def _m07_compact(text: str) -> str:
        """OCR compact 口径:去全部空白 + 小写(空间失真与大小写容忍)。"""
        return "".join(text.split()).lower()

    def _m07_find_row(self, items: list[dict], row_text: str) -> dict | None:
        """OCR 项集合中找平台名行(compact 包含比对)。"""
        key = self._m07_compact(row_text)
        if not key:
            return None
        for it in items:
            if key in self._m07_compact(it["text"]):
                return it
        return None

    @staticmethod
    def _m07_row_band(items: list[dict], row: dict) -> list[dict]:
        """与平台名行 y 向重叠的 OCR 项集合(同一行卡带)。"""
        y1, y2 = row["bbox"][1], row["bbox"][3]
        return [it for it in items if it["bbox"][1] < y2 and it["bbox"][3] > y1]

    @staticmethod
    def _m07_band_state(row: dict, band: list[dict]) -> str:
        """行带授权态:带内出现「未授权」= 未授权,否则已授权。

        未授权行副文案固定含"未授权",已授权行为昵称/角标(sw_平台页 KB)。
        """
        if "未授权" in row["text"]:
            return "unauthorized"
        if any("未授权" in it["text"] for it in band):
            return "unauthorized"
        return "authorized"

    @staticmethod
    def _m07_band_region(row: dict) -> tuple[int, int, int, int]:
        """行带搜索区(模板匹配用):行 y 向扩 30px,x 向放宽由截图裁剪钳制。"""
        _, y1, _, y2 = row["bbox"]
        return (0, max(0, y1 - 30), 3000, (y2 - y1) + 60)

    # ------------------------------------------------------------------
    # 平台页:行授权态探测 / 行体进主页 / [+] 授权钮 / [−] 解绑钮
    # ------------------------------------------------------------------

    def platform_row_state(self, platform: str, timeout: float = 10.0) -> str:
        """平台页某平台行授权态:'authorized' / 'unauthorized' / 'missing'。

        行滚出视口时小步上滑重试(≤400px/步,网易云主页 KB 渐近口径);
        超时未扫到行返回 'missing'(调用方据此 skip/断言)。
        须在平台页调用(音乐分类默认高亮,六平台行首屏可见)。
        """
        row_text = self._m07_row_text(platform)
        deadline = time.monotonic() + timeout
        while True:
            items = self.ocr_scan_page()
            row = self._m07_find_row(items, row_text)
            if row is not None:
                return self._m07_band_state(row, self._m07_row_band(items, row))
            if time.monotonic() >= deadline:
                return "missing"
            self.swipe_up(distance=300)
            self.sleep(0.6)

    def open_platform_home(self, platform: str, home_anchor: str = "",
                           timeout: float = 15.0) -> None:
        """平台页点已授权平台行体进入平台主页并断言到达锚 [OCR]。

        前置:在平台页且目标平台已授权——未授权行体点击无反应
        (swan_平台多级页_* KB 实锤)。授权态非 authorized 时 pytest.skip
        (YAML 数据态闸门 SKIP-NO-ITEM/SKIP-AUTH 语义,授权态自适配)。
        home_anchor 缺省用行文案(平台主页顶栏标题=平台名,同构 QQ/网易)。
        点击落在行标题文字区,天然避开右端 [−] 解绑钮。
        """
        row_text = self._m07_row_text(platform)
        state = self.platform_row_state(platform)
        if state != "authorized":
            pytest.skip(
                f"平台页「{row_text}」行授权态={state}(用例需已授权态,"
                "未授权行体点击无反应;YAML SKIP-NO-ITEM/SKIP-AUTH 闸门)")
        items = self.ocr_scan_page()
        row = self._m07_find_row(items, row_text)
        assert row is not None, (
            f"platform_row_state={state} 但行「{row_text}」[OCR] 消失(页面跳变)")
        self.tap(row["cx"], row["cy"])
        anchor = home_anchor or row_text
        assert self.find_text_by_ocr(anchor, timeout=timeout) is not None, (
            f"点击「{row_text}」行后未进入主页(锚「{anchor}」[OCR] 未命中;"
            "疑主页改版或加载失败)")
        self._wait_list_settled(timeout=4.0)

    def tap_platform_row_plus(self, platform: str, template: str = "",
                              timeout: float = 8.0) -> None:
        """点平台行右侧 [+] 授权钮(授权发起统一入口,前置=该平台未授权)。

        定位链:①template 非空 → 行带 region 内 [图] 匹配;②行带内 OCR
        字形 "+"/"?"(知识库实测 OCR 将方框加号读作 +/?);③均未命中断言
        失败并提示补截模板。已授权行右侧是 [−] 解绑钮——非未授权态直接
        断言失败,防误进解绑确认弹层。
        """
        row_text = self._m07_row_text(platform)
        deadline = time.monotonic() + timeout
        row = band = None
        while True:
            items = self.ocr_scan_page()
            row = self._m07_find_row(items, row_text)
            if row is not None:
                band = self._m07_row_band(items, row)
                break
            if time.monotonic() >= deadline:
                assert False, f"平台页未扫到「{row_text}」行([OCR] 超时)"
            self.swipe_up(distance=300)
            self.sleep(0.6)
        state = self._m07_band_state(row, band)
        assert state == "unauthorized", (
            f"「{row_text}」行授权态={state},[+] 钮仅未授权行存在"
            "(已授权行为 [−] 解绑钮,误点会进解绑确认)")
        if template:
            rect = self.find_image(template, timeout=3,
                                   region=self._m07_band_region(row))
            if rect is not None:
                self.tap(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)
                return
        for it in band:
            glyph = it["text"].strip()
            if glyph in ("+", "?", "+?", "?+", "+/?") or glyph.endswith("+"):
                self.tap(it["cx"], it["cy"])
                return
        assert False, (
            f"「{row_text}」行带内未 OCR 到 [+] 字形(知识库实测方框加号被 "
            "OCR 误读为 +/-/?);需真机补截该行 [+] 模板后回填 template 实参"
            "(见 package_report.json template_needs)")

    def tap_platform_row_minus(self, platform: str, row_template: str = "",
                               timeout: float = 8.0) -> None:
        """点已授权平台行右侧 [−] 解绑钮(解绑确认弹层族入口)。

        定位链:①行带内 OCR 字形 -/−(细横线识别不稳);②row_template
        非空 → 行带 region 内 [图] 匹配行卡后点右缘(模板矩形锚定比例
        定位,非屏幕绝对坐标);③均未命中断言失败并提示补截模板。
        已授权态闸门:未授权行是 [+] 授权钮,误点会发起授权。
        """
        row_text = self._m07_row_text(platform)
        deadline = time.monotonic() + timeout
        row = band = None
        while True:
            items = self.ocr_scan_page()
            row = self._m07_find_row(items, row_text)
            if row is not None:
                band = self._m07_row_band(items, row)
                break
            if time.monotonic() >= deadline:
                assert False, f"平台页未扫到「{row_text}」行([OCR] 超时)"
            self.swipe_up(distance=300)
            self.sleep(0.6)
        state = self._m07_band_state(row, band)
        assert state == "authorized", (
            f"「{row_text}」行授权态={state},[−] 解绑钮仅已授权行存在")
        for it in band:
            glyph = it["text"].strip()
            if glyph in ("-", "−", "–", "_", "-1", "-I", "-l"):
                self.tap(it["cx"], it["cy"])
                return
        if row_template:
            rect = self.find_image(row_template, timeout=3,
                                   region=self._m07_band_region(row))
            if rect is not None:
                self.tap(rect[0] + rect[2] + (rect[3] // 3),
                         rect[1] + rect[3] // 2)
                return
        assert False, (
            f"「{row_text}」行带内未定位到 [−] 解绑钮(细横线 OCR 不稳);"
            "需真机补截该行 [−] 模板后回填 row_template 实参"
            "(见 package_report.json template_needs)")

    # ------------------------------------------------------------------
    # 授权弹层族:确认 / 取消收束 / 静默口径断言
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # 平台主页区块:滚动定位 / QQ 歌手推荐→艺人页(知识库已验证路径)
    # ------------------------------------------------------------------

    def scroll_to_text(self, text: str, max_swipes: int = 6) -> None:
        """小步上滑滚动页面直至 [OCR] 扫到目标文案(平台主页区块可达性兜底)。

        300px/步渐近(网易云主页 KB 口径),每步重扫;max_swipes 滚完仍未
        扫到断言失败(区块缺失/文案变体)。
        """
        for i in range(max_swipes + 1):
            if self.find_text_by_ocr(text, timeout=1) is not None:
                return
            if i < max_swipes:
                self.swipe_up(distance=300)
        assert False, (
            f"滚动 {max_swipes} 屏未扫到「{text}」([OCR];区块缺失或文案变体)")

    def open_qq_artist_page_from_home(self) -> None:
        """QQ 主页「歌手推荐」区块首位头像卡进艺人页(知识库已验证路径)。

        滚动至区块可见 → OCR 扫描标题带下首个艺人头像卡文本项(服务端
        轮换,KB 实测 desc 为 周杰伦/林俊杰/陈奕迅/薛之谦 形态,取首个
        2-4 字非导航文本)并点击 → 断言艺人页骨架(「全部播放」主操作锚,
        swan_艺人页 KB 生效断言;计数 Tab 歌曲/专辑顺序不固定,存在性断言)。
        前置:已在 QQ 音乐主页。
        """
        self.scroll_to_text("歌手推荐")
        items = self.ocr_scan_page()
        title = None
        for it in items:
            if "歌手推荐" in it["text"]:
                title = it
                break
        assert title is not None, "「歌手推荐」区块标题 [OCR] 消失(页面跳变)"
        target = None
        for it in items:
            text = it["text"].strip()
            if it["bbox"][1] <= title["bbox"][3]:
                continue
            if "精选" in text or "视频" in text or text in (">",):
                continue
            if text.isdigit() or len(text) < 2 or len(text) > 4:
                continue
            target = it
            break
        assert target is not None, (
            "「歌手推荐」区块未扫到艺人头像卡文本项(服务端轮换致 desc 缺失;"
            "头像卡 [图] 模板待补截,见 package_report.json template_needs)")
        self.tap(target["cx"], target["cy"])
        assert self.find_text_by_ocr("全部播放", timeout=10) is not None, (
            "点击首位艺人后未进入艺人页(「全部播放」主操作锚未命中)")
        # 计数 Tab 顺序不固定(KB),二者存在性分别断言
        assert self.find_text_by_ocr("歌曲", timeout=5) is not None, (
            "艺人页计数 Tab「歌曲」未命中(骨架渲染不完整)")
        assert self.find_text_by_ocr("专辑", timeout=5) is not None, (
            "艺人页计数 Tab「专辑」未命中(骨架渲染不完整)")

    def confirm_auth_dialog(self, timeout: float = 8.0) -> None:
        """授权确认弹层点「确认」发起授权(授权族第 2 步)。

        确认弹层为未探索面(授权族被知识库禁区拦停),文案以「确认」[OCR]
        为主锚;真机标定后如实际文案不同,改本方法一处即可。
        """
        self.click_text("确认", timeout=timeout)

    def dismiss_auth_popup(self, timeout: float = 5.0) -> None:
        """尽力关闭授权确认/进度/引导弹层(清理用)。

        授权门禁弹层 press_back 一次即关(KB 实测),确认/进度弹层同构
        假设;仅在探测到弹层文案时才动作,避免无弹层时误退平台页。
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.find_text_by_ocr("取消", timeout=1) is not None:
                self.click_text("取消", timeout=2)
                self.sleep(0.8)
                continue
            if self.find_text_by_ocr("确认", timeout=1) is not None:
                self.press_back()
                self.sleep(0.8)
                continue
            break

    def assert_no_auth_error(self) -> None:
        """断言平台页无授权错误类文案(user_cancel 静默口径,坑 6)。

        toast 存活 2-3s,本断言为尽力口径:常驻错误文案(操作失败/授权
        失败)不得出现在平台页;瞬时 toast 漏检局限在用例 docstring 说明。
        """
        self.text_not_exists("操作失败", timeout=2)
        self.text_not_exists("授权失败", timeout=2)

    # ------------------------------------------------------------------
    # 授权发起观察 / 逐级返回收口
    # ------------------------------------------------------------------

    def observe_auth_launch(self, max_wait: float = 25.0) -> bool:
        """点「确认」发起授权后观察跳转发起形态(授权族"至跳转发起"口径)。

        双形态观察:①宿主内授权中进度弹层(授权中/进度/等待文案);②
        第三方应用/商店被拉起(宿主行锚与进度文案同时消失)——此时条件
        press_back 一次拉回(根级禁盲返:仅宿主行锚全消失才退,宿主平台
        页绝不盲返)。返回 True=观察到授权中进度弹层;False=等待窗内
        未捕获(B 口径,进度弹层文案真机标定后收紧,见 template_needs)。
        须在 confirm_auth_dialog 之后调用。
        """
        deadline = time.monotonic() + max_wait
        backed = False
        while time.monotonic() < deadline:
            text = "".join(it["text"] for it in self.ocr_scan_page())
            if "授权中" in text or "进度" in text or "等待" in text:
                return True
            if any(row in text for row in self._M07_ROW_TEXTS.values()):
                self.sleep(1.0)
                continue
            if not backed:
                self.press_back()
                backed = True
                self.sleep(1.5)
                continue
            self.sleep(1.0)
        return False

    def back_to_platform_page(self, max_backs: int = 3) -> None:
        """条件返回直至平台入口页(逐级返回收口,根级禁盲返)。

        每次动作前 OCR 探测平台页锚(任一平台行文案):已在平台页直接
        结束;否则 press_back 一次再探。max_backs 次返回后仍未到达断言
        失败(返回栈异常/页面改版)。全程只读,不改任何授权态。
        """
        row_texts = list(self._M07_ROW_TEXTS.values())
        for i in range(max_backs + 1):
            text = "".join(it["text"] for it in self.ocr_scan_page())
            if any(row in text for row in row_texts):
                return
            if i < max_backs:
                self.press_back()
                self.sleep(1.0)
        assert False, (
            f"条件返回 {max_backs} 次仍未到达平台入口页(平台行锚 [OCR] 全未命中)")
