"""P03 包新增业务方法 mixin（首页 M04 / 搜索 M05 批次转换沉淀）。

纯类，不继承；方法体只调用基础 AW 层（AWBase/FlutterBaseAW/AndroidBaseAW
公开方法）、 SwanBusiness 下划线私有方法（挂入 MRO 后可解析）与本类自有方法。
业务方法组合不进 mixin（checker 规则：self.<x> 仅限基础 AW 层），业务层
公开方法（go_top_tab/search/open_platform 等）一律在测试文件经 self.userA 调用。

集成：挂入 SwanBusiness MRO 由大领导统一做（DIGEST §2.3）。
定位口径：OCR 文本优先；图像模板仅用 image/image_name_mapping.py 已注册常量；
禁坐标、禁运行期 accessibility key、禁硬等待（全部用带 timeout 的探测）。
"""
from __future__ import annotations

import logging

from image.image_name_mapping import (
    SWAN_BOTTOM_PLAYER_BAR,
    SWAN_SEARCH_EMPTY,
    SWAN_SEARCH_SUBMIT,
)

logger = logging.getLogger(__name__)


class SwanRP03Mixin:
    """P03（M04 首页 / M05 搜索）批次新增方法。"""

    # 与 SwanBusiness._RESULTS_TAB_ROW_REGION / _RESULTS_CONTENT_REGION 同值
    # （结果页顶 Tab 行 / 结果内容区，私有镜像，避免依赖未挂 MRO 时的属性）。
    _RESULTS_TAB_ROW_REGION = (0, 190, 720, 130)
    _RESULTS_CONTENT_REGION = (0, 330, 720, 1120)

    # 结果区 OCR 行排除词（Tab 行/分组头/空态文案等非歌曲行）
    _RESULT_ROW_STOP_TEXTS = (
        "单曲", "艺人", "专辑", "歌单", "电台", "播客", "更多", "收起",
        "没有找到相关结果", "QQ音乐", "网易云音乐", "酷狗音乐", "SWAN",
        "搜索歌曲或艺术家等", "跨平台搜索音乐",
    )

    def open_search_input_page(self, bar_image: str = "",
                               ocr_fallback: str = "",
                               timeout: float = 15.0) -> None:
        """从当前顶 Tab 的搜索条进入搜索输入页，并断言输入页到位。

        bar_image 优先（image_name_mapping 已注册常量，实参由用例内联传入）；
        OCR 兜底文案 ocr_fallback 次之（如 '跨平台搜索音乐' / 平台主页
        '搜索QQ音乐'）；两者都不可见时按 search() 现状口径回滚顶部再探
        （镜像 SwanBusiness.search 的 home 分支；已回顶盲滑触发下拉刷新的
        风险与既有实现一致，靠先探测再滑动缓解）。
        结尾断言输入页 hint 文案（YAML/知识库锚点）。
        """
        target = ""
        if bar_image:
            for _ in range(4):
                if self.find_image(bar_image, timeout=1) is not None:
                    target = bar_image
                    break
                if ocr_fallback and self.find_text_by_ocr(
                        ocr_fallback, timeout=1) is not None:
                    target = ocr_fallback
                    break
                self.swipe_down()
            if not target:
                target = bar_image  # 最后一搏按图点击，由 click_image 超时报错
        else:
            assert ocr_fallback, "open_search_input_page 需要 bar_image 或 ocr_fallback 之一"
            target = ocr_fallback
        if target == bar_image and bar_image:
            self.click_image(bar_image, timeout=10)
        else:
            self.click_text(target, timeout=10)
        # 授权通知弹层可能遮在搜索页之上（既有业务私有口径复用）
        self._dismiss_auth_notice_popup()
        self.text_exists("搜索歌曲或艺术家等", timeout=timeout)

    def submit_search_keyword(self, keyword: str,
                              input_anchor: str = "搜索歌曲或艺术家等",
                              timeout: float = 15.0) -> None:
        """搜索输入页输入关键词并提交，断言结果页顶 Tab 行渲染。

        input_anchor 为输入框定位 OCR 文案：默认输入页 hint；结果态/历史态
        改词场景传框内现有关键词（实参由用例内联传入）。输入前先 clear_input
        归零（避免改词场景光标追加拼词），回显断言后再点搜索按钮 [图]，
        以结果顶 Tab 行 [OCR]（'单曲'）确认结果页就绪。
        """
        self.click_text(input_anchor, timeout=10)
        self.clear_input()
        self.input_text(keyword)
        self.text_exists(keyword, timeout=5)
        self.click_image(SWAN_SEARCH_SUBMIT, timeout=10)
        # 结果页就绪探针：有结果→顶 Tab 行 [OCR]；无结果→空态 [图]/[OCR]
        # （账号未授权/无命中词场景同样到达结果页，空态即就绪）
        results_ready = (
            self.find_text_by_ocr("单曲", timeout=timeout,
                                  region=self._RESULTS_TAB_ROW_REGION) is not None
            or self.find_image(SWAN_SEARCH_EMPTY, timeout=3) is not None
            or self.find_text_by_ocr("没有找到相关结果", timeout=2) is not None)
        assert results_ready, "提交后未到达结果页（无结果顶 Tab 行亦无空态标识）"

    def assert_no_anr_dialog(self) -> None:
        """OCR 探测系统 ANR 对话框文案，断言不存在（NEG 守门口径）。

        覆盖中英文系统弹窗常见文案；OCR 扫整屏，弹窗浮于 App 之上可见。
        """
        for text in ("isn't responding", "没有响应", "无响应", "Not Responding"):
            assert self.find_text_by_ocr(text, timeout=1) is None, (
                f"检测到 ANR 对话框文案: {text!r}")

    def enter_search_history_delete_mode(self) -> None:
        """进入搜索历史删除模式（历史区'删除'入口）。

        入口若为无 OCR 文案的图标则当前无法定位（template_needs 已登记
        'swan_搜索输入页_删除图标'），断言失败信息直接指向该缺口。
        """
        if self.find_text_by_ocr("删除", timeout=3) is not None:
            self.click_text("删除", timeout=5)
            return
        assert False, ("历史区删除入口无 OCR 文案且图像模板未注册"
                       "(template_needs: swan_搜索输入页_删除图标)——待补图后"
                       "改用 click_image")

    def play_first_song_result(self, timeout: float = 15.0) -> None:
        """结果页单曲 Tab 点击首个歌曲行开始播放，断言底部播放条出现。

        行选取：结果内容区 OCR 行按 cy 升序取首个非排除词行（排除顶 Tab/
        分组头/空态文案，见 _RESULT_ROW_STOP_TEXTS）；动态 tap 坐标来自
        OCR 匹配（仓内既有惯用法，非硬编码坐标）。
        """
        rows = [i for i in self.ocr_scan_page(region=self._RESULTS_CONTENT_REGION)
                if i["text"].strip()
                and not any(s in i["text"] for s in self._RESULT_ROW_STOP_TEXTS)]
        assert rows, "结果内容区未 OCR 到可点击歌曲行"
        row = min(rows, key=lambda i: i["cy"])
        logger.info("play_first_song_result 点击行: %s", row["text"])
        self.tap(row["cx"], row["cy"])
        assert self.find_image(SWAN_BOTTOM_PLAYER_BAR, timeout=timeout) is not None, (
            "点击歌曲行后底部播放条未出现（播放未拉起或模板漂移）")

    def count_texts_containing(self, prefix: str, max_screens: int = 4) -> int:
        """翻屏收集 OCR 文本，统计含 prefix 的去重条数（历史/列表计数口径）。

        用于搜索历史条数类断言：逐屏 ocr_scan_page 收集含 prefix 的文本，
        按去重文本计数（跨屏重叠行不会重复计数）。OCR 相邻芯片可能并成
        一行导致欠计，属 B 级已知限制（docstring/报告注记）。
        """
        seen = set()
        for _ in range(max_screens + 1):
            for item in self.ocr_scan_page():
                text = item["text"].strip()
                if prefix in text:
                    seen.add(text)
            self.swipe_up()
        return len(seen)

    def tap_first_row_below_anchor(self, anchor: str) -> None:
        """OCR 定位锚点行下方首个可点击行并点击（音乐 Tab 歌单卡直达）。

        用于平台区块头（如 '网易云音乐'）下方首张歌单卡的动态定位；
        排除锚点自身与分组头类文案。
        """
        items = self.ocr_scan_page()
        anchor_rows = [i for i in items if anchor in i["text"]]
        assert anchor_rows, f"未 OCR 到锚点行 {anchor!r}"
        anchor_y = min(i["cy"] for i in anchor_rows)
        below = [i for i in items
                 if i["cy"] > anchor_y + 10 and i["text"].strip()
                 and anchor not in i["text"]
                 and not any(s in i["text"] for s in self._RESULT_ROW_STOP_TEXTS)]
        assert below, f"锚点 {anchor!r} 下方未 OCR 到可点击行（歌单卡）"
        row = min(below, key=lambda i: i["cy"])
        logger.info("tap_first_row_below_anchor 点击行: %s", row["text"])
        self.tap(row["cx"], row["cy"])
