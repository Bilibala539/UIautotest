"""Swan 回归 P07 包(M12 收藏与曲库)业务 mixin —— 域内复用编排。

职责边界(docs/agents/swan/测试用例文件规范.md §2.3 + tcbatch DIGEST):
- 只放 M12 域(歌单/我的收藏/聚合歌单/批量/播放历史)≥2 处复用或复杂编排的方法;
- 方法体仅用基础 AW 原语(find_text_by_ocr/click_text/text_exists/click_image/
  find_image/find_image_rect/image_exists/input_text/clear_input/long_press_text/
  press_back/swipe_up/ocr_scan_page)与本 mixin 自身方法编排;
- 纯类不继承;mixin 挂入 SwanBusiness MRO 由大领导集成时统一处理;
- 严禁改 utils/aw/business/swan.py 及任何既有文件。

页面锚约定(与既有已转正模板对齐,见 image/image_name_mapping.py):
- 我的收藏页:我的音乐分组行 SWAN_FAV_MUSIC_GROUP_ROW / 添加歌单按钮
  SWAN_FAV_ADD_PLAYLIST_BUTTON;
- 歌单页:平台 Tab 行 SWAN_PLAYLIST_TAB_SWAN / 新建按钮
  SWAN_PLAYLIST_CREATE_BTN / 新建弹窗关闭钮 SWAN_PLAYLIST_NEWDLG_CLOSE_BTN;
- 歌单详情页:更多按钮 SWAN_PD_MORE_BTN(既有 open_playlist_detail 的落点锚);
- 播放历史页:顶栏 SWAN_HISTORY_TOPBAR / 分类 Tab 条 SWAN_HISTORY_TABBAR。
"""
from __future__ import annotations

import logging

from image.image_name_mapping import (
    SWAN_FAV_ADD_PLAYLIST_BUTTON,
    SWAN_FAV_MUSIC_GROUP_ROW,
    SWAN_FAVORITE_PLAY_ALL,
    SWAN_HISTORY_TABBAR,
    SWAN_ME_FAVORITES_ROW,
    SWAN_PD_MORE_BTN,
    SWAN_PLAYLIST_CREATE_BTN,
    SWAN_PLAYLIST_NEWDLG_CLOSE_BTN,
    SWAN_PLAYLIST_TAB_SWAN,
    SWAN_TAB_ME,
)

logger = logging.getLogger(__name__)


class SwanRP07Mixin:
    """M12 收藏与曲库域复用编排(基础 AW 原语组装,纯类)。"""

    # ---------------- 探测/点击小工具 ----------------

    def probe_any_text(self, texts, timeout_each: int = 2):
        """逐个 OCR 探测文案(contains 口径),返回第一个命中文案;全未命中返回 None。"""
        for text in texts:
            if self.find_text_by_ocr(text, timeout=timeout_each) is not None:
                return text
        return None

    def click_text_candidates(self, texts, timeout_each: int = 3) -> None:
        """逐个探测并点击第一个命中文案,全未命中断言死亡(带清单报错)。"""
        hit = self.probe_any_text(texts, timeout_each=timeout_each)
        assert hit is not None, f"目标文案均未命中: {list(texts)}"
        self.click_text(hit, timeout=5)

    # ---------------- 页面导航 ----------------

    def open_my_collects_page(self, timeout: float = 15.0) -> None:
        """我的 Tab [图] → 我的收藏行 [图] → 收藏页锚(我的音乐分组行 [图])。"""
        self.click_image(SWAN_TAB_ME, timeout=10)
        self.click_image(SWAN_ME_FAVORITES_ROW, timeout=10)
        assert self.find_image(SWAN_FAV_MUSIC_GROUP_ROW, timeout=timeout) is not None, (
            "未进入我的收藏页(我的音乐分组行 [图] 未命中)")

    def open_composite_segment(self, timeout: float = 10.0) -> None:
        """歌单页 Swans 段点「聚合」chip,切到聚合歌单列表。"""
        self.click_text("聚合", timeout=timeout)

    # ---------------- 歌单创建弹窗族 ----------------

    def open_create_playlist_dialog(self, timeout: float = 10.0) -> None:
        """歌单页新建按钮 [图] → 创建弹窗锚(标题/名称占位/取消任一命中)。"""
        self.click_image(SWAN_PLAYLIST_CREATE_BTN, timeout=timeout)
        hit = self.probe_any_text(
            ("创建歌单", "新建歌单", "歌单名称", "名称", "取消"), timeout_each=2)
        assert hit is not None, "创建歌单弹窗未弹出(标题/名称占位/取消均未命中)"

    def open_collect_create_dialog(self, timeout: float = 10.0) -> None:
        """我的收藏页添加歌单按钮 [图] → 新建歌单弹窗锚(同族弹窗)。"""
        self.click_image(SWAN_FAV_ADD_PLAYLIST_BUTTON, timeout=timeout)
        hit = self.probe_any_text(
            ("创建歌单", "新建歌单", "名称", "取消"), timeout_each=2)
        assert hit is not None, "我的收藏新建歌单弹窗未弹出"

    def close_create_dialog(self) -> None:
        """关闭创建弹窗(关闭钮 [图] 优先,取消/关闭文案兜底),断言弹窗已收。"""
        if self.find_image(SWAN_PLAYLIST_NEWDLG_CLOSE_BTN, timeout=3) is not None:
            self.click_image(SWAN_PLAYLIST_NEWDLG_CLOSE_BTN, timeout=5)
        else:
            self.click_text_candidates(("取消", "关闭"), timeout_each=3)
        assert self.probe_any_text(("创建歌单", "新建歌单", "歌单名称"), timeout_each=2) is None, (
            "创建弹窗未关闭")

    def create_local_playlist(self, name: str, timeout: float = 15.0) -> None:
        """Swans 自建歌单创建:创建弹窗 → 命名 → 保存 → 列表可见。

        前置已在歌单页(创建段);保存钮文案按 l10n playlistSave 口径
        (保存/确定);落列表复核未命中时上滑一屏重探(长列表遮挡兜底)。
        """
        self.open_create_playlist_dialog()
        self.input_text(name)
        self.click_text_candidates(("保存", "确定"), timeout_each=3)
        if self.find_text_by_ocr(name, timeout=8) is None:
            self.swipe_up()
        assert self.find_text_by_ocr(name, timeout=timeout) is not None, (
            f"创建后歌单列表未见新歌单「{name}」")

    def create_composite_playlist(self, name: str) -> None:
        """聚合(关联)歌单创建:创建弹窗 → 关联类型 → 命名 → 保存 →
        来源选择弹层直接完成(0 来源一次性数据口径) → 聚合可见。"""
        self.open_create_playlist_dialog()
        self.click_text("关联", timeout=5)
        self.input_text(name)
        self.click_text_candidates(("保存", "确定"), timeout_each=3)
        hit = self.probe_any_text(("完成", "添加歌单"), timeout_each=3)
        assert hit is not None, "保存后来源选择弹层未拉起(完成/添加歌单均未命中)"
        self.click_text("完成", timeout=5)
        if self.find_text_by_ocr(name, timeout=8) is None:
            self.open_composite_segment()
        assert self.find_text_by_ocr(name, timeout=8) is not None, (
            f"聚合歌单「{name}」创建后列表未见")

    # ---------------- 聚合歌单详情族 ----------------

    def open_composite_detail(self, name: str, timeout: float = 15.0) -> None:
        """打开聚合歌单详情:已在详情(锚命中)时短路;否则 聚合段 → OCR 点行。

        详情锚:添加歌单入口/更多按钮 [图] 任一命中即认定详情已开。
        """
        if self.find_image(SWAN_PD_MORE_BTN, timeout=2) is not None \
                and self.probe_any_text(("添加歌单", "关联"), timeout_each=2) is not None:
            return
        self.open_composite_segment()
        self.click_text(name, timeout=timeout)
        hit = self.probe_any_text(("添加歌单", "首歌"), timeout_each=3)
        assert hit is not None or self.find_image(SWAN_PD_MORE_BTN, timeout=3) is not None, (
            f"聚合歌单「{name}」详情未打开")

    def open_composite_edit_dialog(self, timeout: float = 10.0) -> None:
        """聚合详情 → 更多入口 → 「编辑歌单」 → 编辑弹层锚(三动作任一)。"""
        if self.find_image(SWAN_PD_MORE_BTN, timeout=3) is not None:
            self.click_image(SWAN_PD_MORE_BTN, timeout=5)
        else:
            self.click_text_candidates(("更多",), timeout_each=3)
        self.click_text("编辑歌单", timeout=timeout)
        hit = self.probe_any_text(("改名", "管理歌单", "删除歌单"), timeout_each=3)
        assert hit is not None, "编辑歌单弹层未打开(改名/管理歌单/删除歌单均未命中)"

    def composite_rename(self, new_name: str, timeout: float = 15.0) -> None:
        """编辑弹层 → 改名 → 清空重输 → 保存 → 新名可见(详情页回显)。"""
        self.open_composite_edit_dialog()
        self.click_text("改名", timeout=5)
        self.clear_input()
        self.input_text(new_name)
        self.click_text_candidates(("保存", "确定"), timeout_each=3)
        assert self.find_text_by_ocr(new_name, timeout=timeout) is not None, (
            f"改名后未见新名「{new_name}」")

    def composite_delete_to_confirm(self) -> None:
        """编辑弹层 → 删除歌单 → 断言删除确认弹层出现(停在确认层不提交)。"""
        self.open_composite_edit_dialog()
        self.click_text("删除歌单", timeout=5)
        hit = self.probe_any_text(("确认", "确定", "删除"), timeout_each=3)
        assert hit is not None, "删除确认弹层未出现"

    def composite_delete_confirm(self, name: str, timeout: float = 15.0) -> None:
        """确认弹层点确认,断言聚合从聚合段列表消失(自有一次性数据真删)。"""
        self.click_text_candidates(("确认", "确定"), timeout_each=3)
        if self.find_image(SWAN_PD_MORE_BTN, timeout=2) is not None:
            self.press_back()
        self.open_composite_segment()
        assert self.find_text_by_ocr(name, timeout=timeout) is None, (
            f"聚合歌单「{name}」删除后仍在列表")

    # ---------------- 本地歌单详情菜单族 ----------------

    def delete_playlist_via_detail_menu(self, name: str, timeout: float = 15.0) -> None:
        """歌单详情页更多菜单删除歌单(自有 TEST-SYNTHETIC 数据清理用)。

        更多按钮 [图] → 「删除歌单/删除」 → 确认;删除入口未锚定(详情更多
        菜单族为死代码候选),执行轮探锚后校准;终态:列表不再见该名。
        """
        self.click_image(SWAN_PD_MORE_BTN, timeout=5)
        self.click_text_candidates(("删除歌单", "删除"), timeout_each=3)
        self.click_text_candidates(("确认", "确定"), timeout_each=3)
        if self.find_image(SWAN_PD_MORE_BTN, timeout=2) is not None:
            self.press_back()
        assert self.find_text_by_ocr(name, timeout=timeout) is None, (
            f"歌单「{name}」删除后仍可见")

    def rename_playlist_via_menu(self, new_name: str, timeout: float = 15.0) -> None:
        """歌单详情页更多菜单改名:更多 → 改名/重命名 → 清空重输 → 保存。"""
        self.click_image(SWAN_PD_MORE_BTN, timeout=5)
        self.click_text_candidates(("改名", "重命名"), timeout_each=3)
        self.clear_input()
        self.input_text(new_name)
        self.click_text_candidates(("保存", "确定"), timeout_each=3)
        assert self.find_text_by_ocr(new_name, timeout=timeout) is not None, (
            f"改名后未见新名「{new_name}」")

    # ---------------- 批量/歌曲动作菜单族 ----------------

    def open_batch_mode(self, timeout: float = 10.0) -> None:
        """统一音乐库(我喜欢)页 → 多选入口 → 批量勾选态锚(全选/已选任一)。"""
        self.click_text_candidates(("多选", "批量管理", "批量"), timeout_each=3)
        hit = self.probe_any_text(("全选", "已选"), timeout_each=3)
        assert hit is not None, "未进入批量勾选态(全选/已选均未命中)"

    def open_library_song_menu(self, song: str, timeout: float = 10.0) -> None:
        """我喜欢页对指定歌曲行长按 → 条目动作菜单(锚:添加到歌单类动作)。

        动作菜单形态未探索(卡片坑 1),执行轮探锚后校准。
        """
        self.long_press_text(song, timeout=timeout)
        hit = self.probe_any_text(("添加到歌单", "收藏"), timeout_each=3)
        assert hit is not None, f"歌曲「{song}」动作菜单未打开"

    def open_select_playlist_page(self, timeout: float = 10.0) -> None:
        """歌曲动作菜单 → 「添加到歌单」 → 选择歌单页锚(新建歌单入口任一)。"""
        self.click_text("添加到歌单", timeout=timeout)
        hit = self.probe_any_text(("新建歌单", "选择歌单"), timeout_each=3)
        assert hit is not None, "选择歌单页未打开(新建歌单/选择歌单均未命中)"

    def create_playlist_in_select_page(self, name: str, timeout: float = 15.0) -> None:
        """选择歌单页新建歌单入口 → 命名 → 保存 → 新歌单网格可见。"""
        self.click_text("新建歌单", timeout=5)
        self.input_text(name)
        self.click_text_candidates(("保存", "确定"), timeout_each=3)
        assert self.find_text_by_ocr(name, timeout=timeout) is not None, (
            f"选择歌单页新建后网格未见「{name}」")

    # ---------------- 播放历史页族 ----------------

    def visit_play_history_tabs(self, timeout_each: int = 3) -> int:
        """播放历史页分类 Tab 条 [图] 条带内逐 Tab 点击巡检,返回点击 Tab 数。

        Tab 文案不写死:条带 region OCR 逐项去重点击;Tab 条为页内固定条,
        切 Tab 不影响条带命中。文案全无命中时断言死亡(模板/布局校准点)。
        """
        rect = self.find_image_rect(SWAN_HISTORY_TABBAR, timeout=5)
        assert rect is not None, "播放历史分类 Tab 条 [图] 未命中"
        visited = []
        for item in self.ocr_scan_page(region=rect):
            text = item["text"].strip()
            if not text or text in visited:
                continue
            if self.find_text_by_ocr(text, timeout=timeout_each, region=rect) is not None:
                self.click_text(text, timeout=timeout_each, region=rect)
                visited.append(text)
        assert visited, "分类 Tab 条内无可点击 Tab 文案"
        return len(visited)

    def assert_history_clear_entry_exists(self, timeout: float = 8.0) -> None:
        """播放历史页「清空」入口存在性断言(只断言存在,不点击——禁区 9)。"""
        assert self.find_text_by_ocr("清空", timeout=timeout) is not None, (
            "播放历史页清空入口未找到(OCR「清空」未命中)")

    # ---------------- 我喜欢页(统一音乐库)族 ----------------

    def visit_mylike_page_tabs(self, timeout_each: int = 3) -> list:
        """我喜欢页(统一音乐库)页内 Tab 遍历切换,返回成功点击的 Tab 文案列表。

        Tab 文案未锚定(卡片坑 1,执行轮校准):以播放全部按钮 [图] 上缘为界,
        取其上方 OCR 短文本(≤6 字)为 Tab 候选,逐个探测后点击;每击后以
        播放全部锚 [图] 或「宝藏音乐」口号复核页驻留,双锚皆失按返回键回根。
        候选不足 2 个返回空表(用例层按 SKIP-DATA 口径处理)。
        """
        rect = self.find_image_rect(SWAN_FAVORITE_PLAY_ALL, timeout=6)
        assert rect is not None, "我喜欢页锚(播放全部 [图])未命中"
        candidates = []
        for item in self.ocr_scan_page():
            text = item["text"].strip()
            if not text or len(text) > 6 or text in candidates:
                continue
            if item["cy"] < rect["cy"]:
                candidates.append(text)
        visited = []
        for text in candidates:
            if self.find_text_by_ocr(text, timeout=timeout_each) is None:
                continue
            self.click_text(text, timeout=timeout_each)
            visited.append(text)
            if self.find_image(SWAN_FAVORITE_PLAY_ALL, timeout=3) is None \
                    and self.find_text_by_ocr("宝藏音乐", timeout=2) is None:
                self.press_back()
        return visited
