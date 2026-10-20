"""SwanRP10Mixin —— tcbatch P10 包新增业务方法(M17 权益中心 + M18 QQ 视频域)。

仅本包复用;挂入 SwanBusiness MRO 由集成方统一完成(不改任何既有文件)。
方法体内只用基础 AW 层能力(click_text/find_text_by_ocr/ocr_scan_page/
click_image/press_back/swipe_up/input_text/clear_input/tap/take_screenshot/
find_image)与本类自有方法,不依赖其他业务方法。

B 轨口径:QQ 视频分类页为 push 页且账号授权态运行时才可知,区域常量为
720x1600 口径的布局区提示(仅收窄 OCR 搜索范围,非坐标定位),待真机校准。
"""
from __future__ import annotations

import os

from image.image_name_mapping import (
    SWAN_PLATFORM_NETEASE_ROW,
    SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
    SWAN_TAB_ME,
    SWAN_TAB_PLATFORM,
)
from image.image_name_mapping import image_path


class SwanRP10Mixin:
    """P10 包(M17 设置/平台通道 + M18 视频与投屏)新增业务方法。"""

    # 视频分类页布局区(720x1600 口径,待真机校准;region 仅收窄 OCR 范围)
    _VIDEO_TOP_REGION = (0, 40, 720, 130)        # 顶部搜索条
    _VIDEO_TAB_REGION = (0, 130, 720, 300)       # 六 Tab 条
    _VIDEO_CONTENT_REGION = (0, 300, 720, 1150)  # MV 列表区(避开贴底播放条)

    # 六 Tab 文案与列表区需排除的短词(卡片标题/艺人名不该命中)
    _VIDEO_TAB_LABELS = ("推荐", "内地", "韩国", "港台", "日本", "欧美")
    _VIDEO_NON_CARD_TEXTS = _VIDEO_TAB_LABELS + ("搜索", "投放", "MV", "视频")

    # ==================== M17:权益中心(新协议 AppBridge 容器) ====================

    def open_rights_center_from_tab(self) -> None:
        """从我的页打开权益中心(settings-POS-008 前置链)。

        链路:我的 tab [图] -> 功能行「我的权益」[OCR](找不到则上滑一屏重试,
        知识库:我的页列表项可能被贴底播放条遮挡) -> 容器页锚「权益中心」
        [OCR] 断言(H5 装载完成粗判据;加载域/双桥隔离为日志断言面,不在 UI 轨)。
        """
        self.click_image(SWAN_TAB_ME, timeout=10)
        if not self._find_and_click_scrolled("我的权益"):
            assert False, "我的页未找到「我的权益」功能行 [OCR](已上滑重试)"
        assert self.find_text_by_ocr("权益中心", timeout=20) is not None, (
            "点击「我的权益」后未见到权益中心容器页锚「权益中心」[OCR]——"
            "疑 H5 未装载或容器标题文案待校准(template_needs 已登记)")

    def close_rights_center(self) -> None:
        """退出权益中心回我的页(settings-POS-008 cleanup)。"""
        self.press_back()
        assert self.find_text_by_ocr("我的权益", timeout=10) is not None, (
            "退出权益中心后未回到我的页(「我的权益」行 [OCR] 未命中)")

    # ==================== M18:QQ 视频分类页 ====================

    def open_qq_video_classify(self) -> bool:
        """进入 QQ 视频分类页;未授权返回 False(由用例 pytest.skip)。

        链路:平台 tab [图] -> 平台页锚(网易云行两态 [图] 任一) -> 未授权探针
        (网易云行未授权态 [图] = 全平台未授权,既有样例同口径) -> QQ 行
        [OCR] -> 授权门禁弹层探针(变体 B「请先登录」[OCR],命中则 press_back
        关闭并返回 False) -> QQ 主页锚「搜索QQ音乐」[OCR] -> 「视频」入口
        [OCR](找不到上滑重试) -> 分类页锚:六 Tab 文案 [OCR] 断言。
        返回 True = 已落在视频分类页。
        """
        self.click_image(SWAN_TAB_PLATFORM, timeout=10)
        assert (self.find_image(SWAN_PLATFORM_NETEASE_ROW, timeout=5) is not None
                or self.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                                   timeout=5) is not None), (
            "未到达平台页(网易云行两态 [图] 均未命中)")
        if self.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                           timeout=3) is not None:
            return False
        self.click_text("QQ音乐", timeout=10)
        if self.find_text_by_ocr("请先登录", timeout=4) is not None:
            self.press_back()  # 关授权门禁弹层(知识库:press_back 一次即关)
            return False
        assert self.find_text_by_ocr("搜索QQ音乐", timeout=10) is not None, (
            "点击 QQ音乐行后未见到主页锚「搜索QQ音乐」[OCR]——疑 QQ 未授权"
            "(行体点击无反应)或页面改版")
        if not self._find_and_click_scrolled("视频"):
            assert False, ("QQ 主页未找到「视频」入口 [OCR](已上滑重试;入口"
                           "形态待真机校准,template_needs 已登记)")
        assert self.find_text_by_ocr("推荐", timeout=10,
                                     region=self._VIDEO_TAB_REGION) is not None, (
            "点击「视频」入口后未见到分类页 Tab 锚「推荐」[OCR]")
        return True

    def assert_video_search_bar(self) -> None:
        """分类页顶部搜索条渲染断言(video-POS-001 要素二)。"""
        assert self.find_text_by_ocr("搜索", timeout=5,
                                     region=self._VIDEO_TOP_REGION) is not None, (
            "分类页顶部未见到搜索条 [OCR]")

    def assert_video_tab_order(self, *tabs: str) -> None:
        """六 Tab 全序列顺序断言:逐个 [OCR] 定位并校验 x 坐标严格递增。

        用法:assert_video_tab_order('推荐', '内地', '韩国', '港台', '日本', '欧美')。
        末两项「日本/欧美」顺序锁点即由序列尾部承载(video-POS-002 步骤 2)。
        """
        assert len(tabs) >= 2, "至少传入两个 Tab 文案才能做顺序断言"
        prev_x = -1
        for tab in tabs:
            pos = self.find_text_by_ocr(tab, timeout=5,
                                        region=self._VIDEO_TAB_REGION)
            assert pos is not None, f"分类页 Tab 条未找到「{tab}」[OCR]"
            assert pos[0] > prev_x, (
                f"Tab 顺序异常:「{tab}」x={pos[0]} 未严格递增(前值 {prev_x})")
            prev_x = pos[0]

    def cycle_video_tabs(self, *tabs: str) -> None:
        """逐 Tab 点击切换并断言列表随 type 刷新(video-POS-002 步骤 3)。

        每 Tab 点击后以 MV 列表非空(卡片标题 [OCR] 可读)作为列表已刷新证据。
        """
        for tab in tabs:
            pos = self.find_text_by_ocr(tab, timeout=5,
                                        region=self._VIDEO_TAB_REGION)
            assert pos is not None, f"分类页 Tab 条未找到「{tab}」[OCR]"
            self.tap(pos[0], pos[1])
            assert self.first_video_card_title(), (
                f"点击 Tab「{tab}」后列表为空(卡片标题 [OCR] 未命中)")

    def assert_video_list_loaded(self) -> str:
        """分类/搜索列表非空断言,返回首个卡片标题(video-POS-003/POS-001)。"""
        title = self.first_video_card_title()
        assert title, "MV 列表为空(内容区 [OCR] 未读到任何卡片标题)"
        return title

    def first_video_card_title(self) -> str:
        """读内容区首个 MV 卡片标题(运行时数据,供后续点击与标题断言)。

        口径:内容区 [OCR] 全量扫描,按 y 排序取第一条非 Tab/功能词、
        长度>=2 的文本行;读不到返回空串(由调用方断言)。
        """
        items = self.ocr_scan_page(region=self._VIDEO_CONTENT_REGION)
        rows = sorted(items, key=lambda it: it["bbox"][1])
        for row in rows:
            text = (row.get("text") or "").strip()
            if len(text) < 2:
                continue
            if any(bad in text for bad in self._VIDEO_NON_CARD_TEXTS):
                continue
            return text
        return ""

    def tap_video_card(self, title: str) -> None:
        """点播指定 MV 卡片并以横屏落页断言播放页已开(video-POS-005)。

        视频播放页强制横屏(方向协调器 enterLandscape),截图宽>高即为
        播放页打开的可观察证据;title 为 first_video_card_title 返回的
        运行时数据(非常量中间变量)。
        """
        pos = self.find_text_by_ocr(title, timeout=10)
        assert pos is not None, f"列表中未找到卡片标题「{title}」[OCR]"
        self.tap(pos[0], pos[1])
        self.assert_landscape_orientation()

    def tap_video_card_twice(self, title: str) -> None:
        """650ms 内连点同一 MV 卡片(video-NEG-006 冷却守卫触发)。"""
        pos = self.find_text_by_ocr(title, timeout=10)
        assert pos is not None, f"列表中未找到卡片标题「{title}」[OCR]"
        self.tap(pos[0], pos[1])
        self.tap(pos[0], pos[1])

    def assert_landscape_orientation(self) -> None:
        """断言当前为横屏(截图宽>高;方向协调器进页横屏的可观察证据)。"""
        img = self.take_screenshot()
        assert img is not None, "截图失败,无法断言横屏"
        assert img.shape[1] > img.shape[0], (
            f"当前非横屏(截图 {img.shape[1]}x{img.shape[0]})——播放页未打开"
            "或方向协调器未生效")

    def assert_portrait_orientation(self) -> None:
        """断言当前为竖屏(M18 禁区 4:退出播放页后一级页必须竖屏无残留)。"""
        img = self.take_screenshot()
        assert img is not None, "截图失败,无法断言竖屏"
        assert img.shape[0] > img.shape[1], (
            f"当前非竖屏(截图 {img.shape[1]}x{img.shape[0]})——退出播放页后"
            "横屏残留,方向恢复守卫未生效")

    def exit_video_player_restore_check(self) -> None:
        """退出播放页并做 M18 禁区 4 收尾铁律:竖屏恢复 + 落回分类页。

        同时是 video-NEG-006 的守卫断言载体:连点守卫生效时仅压栈一页,
        单次 press_back 即落回一级页(竖屏);若守卫失效会残留第二层播放页
        (仍横屏),竖屏断言即失败。
        """
        self.press_back()
        self.assert_portrait_orientation()
        assert self.find_text_by_ocr("推荐", timeout=10,
                                     region=self._VIDEO_TAB_REGION) is not None, (
            "退出播放页后未落回分类页(Tab 锚「推荐」[OCR] 未命中)")

    # ==================== M18:视频搜索态 ====================

    def open_video_search(self, keyword: str) -> None:
        """分类页搜索条输入关键词并断言搜索结果渲染(video-POS-004)。

        防抖请求(music/search type=10)为服务端行为:以结果标题命中关键词
        [OCR] 作为搜索态数据源已切换的证据。
        """
        pos = self.find_text_by_ocr("搜索", timeout=5,
                                    region=self._VIDEO_TOP_REGION)
        assert pos is not None, "分类页顶部未找到搜索条 [OCR]"
        self.tap(pos[0], pos[1])
        assert self.input_text(keyword), "关键词输入失败"
        assert self.find_text_by_ocr(keyword, timeout=15) is not None, (
            f"搜索关键词「{keyword}」后未见结果渲染(防抖请求未回或无结果)")

    def clear_video_search(self) -> None:
        """清空搜索关键词并断言数据源切回分类态(video-POS-004 收尾)。"""
        assert self.clear_input(), "搜索词清空失败"
        assert self.find_text_by_ocr("推荐", timeout=10,
                                     region=self._VIDEO_TAB_REGION) is not None, (
            "清空关键词后未回到分类态(六 Tab 条 [OCR] 未命中)")

    # ==================== M18:投屏设备选择弹层(只读探针) ====================

    def open_cast_sheet(self) -> str:
        """打开分类页右上角投放弹层,返回命中的弹层锚文案。

        M18 禁区 1:只开弹层观察,绝不选择设备、绝不触发投屏连接。
        弹层锚待真机校准(候选:完成/取消/本地),template_needs 已登记;
        命中任一即认为弹层已弹出。
        """
        pos = self.find_text_by_ocr("投放", timeout=5)
        assert pos is not None, "分类页未找到投放入口「投放」[OCR]"
        self.tap(pos[0], pos[1])
        anchor = self.probe_first_text(("完成", "取消", "本地"), timeout=8)
        assert anchor, ("点击投放后未见投屏弹层锚(完成/取消/本地)——"
                        "弹层形态待真机校准")
        return anchor

    def dismiss_cast_sheet_check_route(self) -> None:
        """点返回关闭投放弹层并断言路由未变(video-POS-008 取消分轨)。

        双取消分轨中 dismiss 不清路由:关闭后仍停在分类页(六 Tab 在)。
        """
        self.press_back()
        assert self.find_text_by_ocr("推荐", timeout=10,
                                     region=self._VIDEO_TAB_REGION) is not None, (
            "关闭投放弹层后未回到分类页(路由被意外变更)")

    # ==================== 本包通用小工具 ====================

    def probe_first_text(self, texts, timeout: int = 8) -> str:
        """依次探测多候选文案,返回第一个命中的文案(弹层锚/页面锚粗判据)。"""
        for text in texts:
            if self.find_text_by_ocr(text, timeout=timeout) is not None:
                return text
        return ""

    def _find_and_click_scrolled(self, text: str, attempts: int = 3) -> bool:
        """[OCR] 找文案点击;找不到上滑一屏重试(遮挡/折叠场景)。"""
        for _ in range(attempts):
            pos = self.find_text_by_ocr(text, timeout=3)
            if pos is not None:
                self.tap(pos[0], pos[1])
                return True
            self.swipe_up()
        return False

    # ==================== M17:切服弹层(Logo 入口,B 轨模板门禁) ====================

    # 切服 Logo 入口模板(draft 路径;截获入库前按「模板未截获」条件 skip)
    _ABOUT_SERVER_LOGO = image_path("swan_关于我们页_切服Logo.png",
                                    platform="flutter", draft=True)

    def open_about_detail(self) -> None:
        """我的页进入关于与升级页并打开「关于我们」三级页(切服弹层前置链)。

        链路(知识库 swan_关于与升级页):我的 tab [图] -> 上滑两屏(列表项
        被贴底播放条遮挡) -> 「关于与升级」行 [OCR] -> 「关于我们」行 [OCR]。
        三级页(/me/about/detail)未探索无 OCR 锚,弹层入口由
        probe_tap_server_logo 的模板探测承载(template_needs 已登记)。
        """
        self.click_image(SWAN_TAB_ME, timeout=10)
        self.swipe_up()
        self.swipe_up()
        pos = self.find_text_by_ocr("关于与升级", timeout=5)
        assert pos is not None, "我的页上滑两屏后未找到「关于与升级」行 [OCR]"
        self.tap(pos[0], pos[1])
        pos = self.find_text_by_ocr("关于我们", timeout=8)
        assert pos is not None, "关于与升级页未找到「关于我们」行 [OCR]"
        self.tap(pos[0], pos[1])

    def probe_tap_server_logo(self) -> bool:
        """探测并点击切服弹层 Logo 入口,返回弹层是否弹出(用例据此条件 skip)。

        Logo 为 198×80 图像资产无 OCR 文案且模板未截获:文件未入库时按
        「模板未截获」返回 False(同 probe_image 缺失防护口径,不炸用例);
        模板就绪后点击并探测弹层标题「选择服务器」[OCR]——未弹出返回 False
        (Release 包无手势属设计现状/弹层锚文案待校准),由用例运行期条件
        skip,不算误转。
        """
        if not os.path.exists(self._ABOUT_SERVER_LOGO):
            return False
        rect = self.find_image_rect(self._ABOUT_SERVER_LOGO, timeout=5)
        if rect is None:
            return False
        self.tap(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)
        return self.find_text_by_ocr("选择服务器", timeout=8) is not None

    def assert_server_switch_sheet(self) -> None:
        """切服弹层展示断言(禁区 1:只断言展示,绝不点击任何环境选项)。

        选项文案取 YAML l10n 锚:测试服/正式服/本地环境(NEG-005 口径作
        「本地服」,第三项双候选探测)。M17 禁区 1:真实切服会立即本地登出
        清 token,选项一律不可点。
        """
        for text in ("测试服", "正式服"):
            assert self.find_text_by_ocr(text, timeout=5) is not None, (
                f"切服弹层未命中选项「{text}」[OCR]")
        assert self.probe_first_text(("本地环境", "本地服"), timeout=5), (
            "切服弹层未命中第三选项(本地环境/本地服) [OCR]")

    def close_server_switch_sheet(self) -> None:
        """返回关闭弹层并退回关于与升级页(不选任何项,零切服零登出)。

        双 press_back:弹层 -> 三级页 -> 关于与升级页;「关于与升级」标题
        [OCR] 命中即仍停留在 App 内层页(登录态未被切服/登出打断的证据)。
        """
        self.press_back()
        self.press_back()
        assert self.find_text_by_ocr("关于与升级", timeout=8) is not None, (
            "关闭切服弹层后未退回关于与升级页(弹层未关或发生意外跳转)")
