"""P05 批次（M08 电台/播客 + M16 推送/日活/版本）新增业务 mixin。

tcbatch 批量转换新增方法统一沉淀于此（禁改 swan.py 等现有文件）；
挂入 SwanBusiness MRO 后经 user 对象代理（self.userA.<方法>）使用。
方法体只允许自调用基础 AW 层方法（click_text/find_text_by_ocr/
ocr_scan_page/tap/swipe_up/press_back/wait_toast/click_image 等），
与 swan.py/swan_regression.py 现有方法不重名。
"""
from __future__ import annotations

from image.image_name_mapping import (
    SWAN_PLATFORM_RADIO_ROW_ARROW,
)


class SwanRP05Mixin:
    """P05 批次新增可复用方法（radio 页族 l10n 中文锚未核准，候选列表兜底）。

    radio 页族 HiviTestIds=0（卡片坑 12），定位一律 l10n 文本 OCR +
    页面结构兜底；其中文案的中文串真机未核准，相关方法一律收候选
    文案列表（见 P05 package_report.template_needs 登记）。
    """

    def click_any_text(self, *texts, timeout: int = 10) -> str:
        """候选文案依次探测并点击首个命中者，返回命中文案。

        用于锚点中文串不确定（l10n key 已知、zh 未见真机核准）的入口
        点击：首个候选给足 timeout，其余快速轮询，避免 4 候选 x 10s
        的全量等待。
        """
        for idx, text in enumerate(texts):
            wait = timeout if idx == 0 else 2
            pos = self.find_text_by_ocr(text, timeout=wait)
            if pos is not None:
                self.tap(pos[0], pos[1])
                return text
        raise AssertionError(f"候选文案均未出现: {list(texts)}")

    def assert_any_of_texts(self, *texts, timeout: int = 10) -> str:
        """候选文案存在性断言（不点击），返回命中文案。

        期望文本取自 YAML expect 的真实 UI 文案；l10n 中文未核准时收
        候选列表，任一命中即通过，全落空报 AssertionError。等待策略同
        click_any_text（首候选足时、余候选快轮询）。
        """
        for idx, text in enumerate(texts):
            wait = timeout if idx == 0 else 2
            if self.find_text_by_ocr(text, timeout=wait) is not None:
                return text
        raise AssertionError(f"候选文案均未出现: {list(texts)}")

    def ocr_page_texts(self, region=None) -> list:
        """当前页 OCR 全量文本列表（过滤空串；item 结构见 aw_base.ocr_scan_page）。

        列表页无稳定标题锚时的可观察状态兜底：渲染项计数/内容集合
        diff（radio-POS-009 分页追加、radio-POS-010 分类重置复用）。
        """
        return [item.get("text", "").strip()
                for item in self.ocr_scan_page(region)
                if item.get("text", "").strip()]

    def tap_card_by_texts(self, *texts, scrolls: int = 3,
                          timeout: int = 4) -> str:
        """滚动查找并点击候选文案卡片/行，返回命中文案。

        radio 页族 0 testId、卡片标题动态（电台名/分类名/城市名），同
        swan._tap_song_row_by_ocr 口径：OCR 扫描取文字中心后运行时
        tap（禁硬编码坐标）；每轮扫描不中则上滑一屏再试，首轮不滚动
        （目标常在首屏）。
        """
        for _ in range(scrolls + 1):
            for text in texts:
                pos = self.find_text_by_ocr(text, timeout=timeout)
                if pos is not None:
                    self.tap(pos[0], pos[1])
                    return text
            self.swipe_up()
        raise AssertionError(f"滚动 {scrolls} 屏未找到候选卡片: {list(texts)}")

    def tap_first_list_item(self, *exclude, min_len: int = 4) -> str:
        """点击列表区首个非界面框架文案的动态内容行，返回所点文案。

        电台名/城市名等运行时数据无静态锚（TEST-SYNTHETIC 选择语义：
        取列表首个可用项），OCR 扫描过滤界面框架文案后取首个长文本项
        点击（同 _tap_song_row_by_ocr 运行时 tap 口径，禁硬编码坐标）。
        exclude 传页面特有框架词（如城市页「选择城市」「热门城市」）。
        """
        chrome = {"全部", "城市", "电台", "搜索", "全国电台", "国家台",
                  "加载中", "没有更多"} | set(exclude)
        for item in self.ocr_scan_page():
            text = (item.get("text") or "").strip()
            if len(text) < min_len or text in chrome:
                continue
            if any(w in text for w in ("搜索", "电台分类", "推荐")):
                continue
            self.tap(item["cx"], item["cy"])
            return text
        raise AssertionError("页面无可点击的动态内容行")

    def radio_open_hub_from_platform(self) -> None:
        """平台页经电台行进入电台 Hub 路由页（POS-001/POS-002 复用）。

        平台页电台行 0 testId，唯一可达锚为已登记的行箭头图模板
        （image_name_mapping.SWAN_PLATFORM_RADIO_ROW_ARROW）；行内
        l10n 中文未核准，点击后按候选文案断言 Hub 到位。
        """
        self.click_image(SWAN_PLATFORM_RADIO_ROW_ARROW, timeout=10)
        self.assert_any_of_texts("电台分类", "全国电台", "电台", timeout=10)

    def dismiss_update_dialog_guarded(self) -> None:
        """「软件升级」弹窗守卫：非强更弹窗点「稍后更新」关闭。

        弹窗只有「立即更新」无「稍后更新」即为强更（按禁区约定禁点
        「立即更新」——会拉起下载中断后续断言），运行时 skip 转人工；
        非强更弹窗点「稍后更新」关闭后继续。push-POS-001/POS-003 复用。
        """
        if self.find_text_by_ocr("立即更新", timeout=2) is None:
            return
        if self.find_text_by_ocr("稍后更新", timeout=2) is None:
            import pytest

            pytest.skip("强更弹窗无「稍后更新」钮，按禁区不点「立即更新」，转人工")
        self.click_text("稍后更新", timeout=5)
