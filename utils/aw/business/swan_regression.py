"""Swan 回归用例公共前置与清理 mixin（原 tests/flutter/swan_regression_common*.py，
2026-10-09 迁入 business 层；2026-10-12 一用例一文件拆分时新增登录域 mixin）。

非用例模块（无 test_ 前缀，pytest 与 run_parallel 均不收集）。
三个 mixin 同文件分层：
- SwanPlayerRegressionMixin    播放器域（播放发起/控制/设备切换/进度音量用例共用）
- SwanContentRegressionMixin   导航/收藏历史/搜索域（继承前者，仅覆写 teardown），
  三用例收尾态常在 push 页（歌单详情/播放历史/搜索结果），这些页无底部 4 tab，
  teardown 需要「收播放页 -> 逐级 press_back 退出 push 页 -> 回全局 tab 壳 ->
  go_home」的反向退出序列，与播放器域 teardown 结构不同
- SwanLoginRegressionMixin     登录域存量用例（登录/登出、密码登录、只读页，
  断言走 key 的存量实现，口径见类 docstring）

新代码定位一律图像模板 > OCR 文本（方案 §0）；2026-10-12 起导航域存量
key 已迁移 [图]（go_home / go_bottom_tab / _open_device_page，W1-A 第一批，
设备 Tab 点击改 SWAN_TAB_DEVICE [图]），剩余 key 仅登录域
（SwanLoginRegressionMixin 断言辅助 + login 系方法，迁移待第二批，
见 docs/待办与缺口清单.md「定位策略定稿」节）。

rig 环境变量（均可在不配置时走默认/skip）：
- SWAN_DEVICE_NAME  rig WiFi 音箱设备名（默认 Libretto_0E00，知识库实测绑定设备）
- SWAN_TEST_SONG    我喜欢歌单中的歌曲名（用例14 单曲播放；未配置则 skip；
                    歌曲类历史断言复用）
- SWAN_FAV_PLATFORMS       用例41-43 平台代码列表，逗号分隔（默认 swan；
                           第三方平台须授权态，见方案 §5⑤）
- SWAN_COLLECT_PLATFORMS   用例44-55 目标歌单平台代码列表（默认 swan）
- SWAN_COLLECT_PLAYLIST    用例44-55 目标歌单名（默认 我的音乐；收藏结果
                           由 remove_song_from_playlist 垃圾桶预清理回滚，
                           run6 可重复性设计，见 SwanBusiness
                           .remove_song_from_playlist 注记）
- SWAN_COLLECT_PLAYER_SONG 用例44-55 source="player" 分支的收藏曲（默认
                           回落 SWAN_TEST_SONG；run5 改版——原「播放全部
                           首曲」疑已在目标歌单触发重复收藏拦截，改为点
                           名播放指定曲；run6 起预清理自动移除往轮残留，
                           任意歌可重复收藏，见 test_collect_song 注）
- SWAN_COLLECT_SOURCE_PLAYLIST
                           用例44-55 source="playlist_page" 的收藏源歌单
                           （默认 我的家庭）。run6 起预清理运行时强制
                           「顶行曲不在目标歌单内」（收藏前先经垃圾桶移除），
                           不再依赖 rig 数据态，仅须该歌单含 ≥1 首歌；
                           rig 数据变化（清空/改名）时用本变量覆盖
- SWAN_HISTORY_PLAYLIST / SWAN_HISTORY_ARTIST / SWAN_HISTORY_ALBUM /
  SWAN_HISTORY_RADIO / SWAN_HISTORY_PODCAST
                           用例56-68 各分类断言条目名（未配置该类 skip）；
                           歌曲类复用播放器域 SWAN_TEST_SONG，配置
                           SWAN_HISTORY_FRESH_PLAY=1 时现场播放造历史数据
- SWAN_SEARCH_KEYWORD_<tab> 用例69-72 各分类搜索关键词（默认 piano，
                           英文；adb 中文输入不可达）
- SWAN_SEARCH_PLATFORMS    已授权平台代码列表，逗号分隔（如 "qq,netease"；
                           配置后 assert_search_results 对所列平台断言
                           「有结果」，账号 B 已授权口径；默认空 -> 断言
                           空态，干净未授权账号稳定态。两种口径见
                           SwanBusiness.assert_search_results docstring）
"""
from __future__ import annotations

import logging
import os
import time

from image.image_name_mapping import (
    SWAN_BOTTOM_PLAYER_BAR,
    SWAN_DEVICE_ADD_BTN,
    SWAN_DEVICE_SHEET_TITLE,
    SWAN_FAVORITE_PLAY_ALL,
    SWAN_HOME_TAB_AI,
    SWAN_HOME_TAB_MUSIC,
    SWAN_HOME_TAB_RADIO,
    SWAN_HOME_TAB_RECOMMEND,
    SWAN_LOGIN_PASSWORD_ENTRY,
    SWAN_LOGIN_PRIVACY_POLICY_LINK,
    SWAN_LOGIN_SUBMIT_BTN,
    SWAN_PASSWORD_FIELD,
    SWAN_PWD_SMS_TOGGLE,
    SWAN_PLAYER_PAUSE_BTN,
    SWAN_PLAYER_VOLUME_POPUP,
    SWAN_TAB_DEVICE,
    SWAN_TAB_HOME,
    SWAN_TAB_ME,
    SWAN_TAB_PLATFORM,
)

logger = logging.getLogger(__name__)

DEVICE_TYPES = ["speaker", "wifi_device"]  # speaker=手机扬声器默认输出 / wifi_device=rig 音箱


class SwanPlayerRegressionMixin:
    """播放器域回归用例 mixin：登录/导航/播放前置与 G3/G4 清理。

    与 BaseTest 一起继承（mixin 放前），setup/teardown 由 conftest 的
    _auto_test_lifecycle 自动调用。
    """

    DEVICE_NAME = os.environ.get("SWAN_DEVICE_NAME", "Libretto_0E00")
    SONG_NAME = os.environ.get("SWAN_TEST_SONG", "")

    # 登录页锚（均已转正）：「下一步」按钮 / 隐私政策链接任一可见即在登录页
    _LOGIN_PAGE_TEMPLATES = (SWAN_LOGIN_SUBMIT_BTN, SWAN_LOGIN_PRIVACY_POLICY_LINK)
    # 首页壳主锚：全局底部导航 4 图标（未选中态，已转正、verify 跨机实测 1.0；
    # 首页/平台/设备/我的 4 个一级页至多 1 个 Tab 选中，任一可见即在首页壳）
    _BOTTOM_NAV_TEMPLATES = (SWAN_TAB_HOME, SWAN_TAB_PLATFORM,
                             SWAN_TAB_DEVICE, SWAN_TAB_ME)
    # 首页壳兜底锚：顶 Tab 未选中态图（Wave1 图跨机失配 0.35-0.71，
    # aw-element 重截中，verify 首跑结论降为最后轮询项）
    _TOP_TAB_TEMPLATES = (SWAN_HOME_TAB_RECOMMEND, SWAN_HOME_TAB_MUSIC,
                          SWAN_HOME_TAB_RADIO, SWAN_HOME_TAB_AI)
    # 底部播放条 OCR 兜底条带 (x, y, w, h)：720x1612 屏实测播放条位于
    # y≈1376-1476（verify-run3 after_relaunch_full.png 模板定位+裁片目视，
    # 模板本身 720x100 全宽条带），上下留少量容差；上边界务必低于
    # y≈1500 起的全局底部导航图标行，防止误点「首页/平台/设备/我的」
    _BOTTOM_BAR_REGION = (0, 1370, 720, 116)

    # ---------- 锚点探测（模板缺失防护 + 首页壳判据） ----------

    def probe_image(self, template: str, timeout: int = 1,
                     threshold: float = 0.8) -> tuple[int, int] | None:
        """模板文件在盘才 find_image；缺失记日志按未命中处理。

        AWBase.find_image 对缺失模板文件是 assert 崩溃而非返回 None（框架层
        行为，已单独上报），清理/锚点探测这类「可选命中」调用先 os.path.exists
        防护（常量为绝对路径），避免模板未入库（如 SWAN_PLAYER_PAUSE_BTN，
        需授权平台+播放任务才能截）时炸掉 teardown。
        threshold 供失配模板的低阈值探测使用（见 _close_volume_popup_if_any）。
        """
        if not os.path.exists(template):
            logger.warning("模板图未入库，按未命中跳过: %s", template)
            return None
        return self.user.find_image(template, timeout=timeout, threshold=threshold)

    def _login_page_on_screen(self, timeout: int = 1) -> bool:
        """登录页锚：「下一步」按钮 / 隐私政策链接图任一可见。"""
        return any(self.probe_image(template, timeout=timeout) is not None
                   for template in self._LOGIN_PAGE_TEMPLATES)

    def _home_nav_visible(self, timeout: int = 1) -> bool:
        """首页壳主锚：底部导航 4 图任一可见（已转正、跨机稳健，verify 实测 1.0）。"""
        return any(self.probe_image(template, timeout=timeout) is not None
                   for template in self._BOTTOM_NAV_TEMPLATES)

    def _wait_home_shell(self) -> None:
        """断言已到首页壳：主底部导航 4 图 → 辅 OCR「推荐」→ 兜底顶 Tab 图。"""
        if self._home_nav_visible(timeout=3):
            return
        if self.user.find_text_by_ocr("推荐", timeout=3) is not None:
            return
        for template in self._TOP_TAB_TEMPLATES:
            if self.probe_image(template, timeout=2) is not None:
                return
        assert False, "未进入首页壳（底部导航 4 图 / OCR「推荐」/ 顶 Tab 未选中态图均未命中）"

    # ---------- 登录与导航 ----------

    def ensure_logged_in_on_home(self) -> None:
        """幂等登录并断言在首页壳（登录复用存量 login_by_sms；到位断言用图片）。

        进入前防护（verify 首跑结论）：登录页锚与首页壳锚均不可见（App 停在
        播放页等未知页）时先 relaunch_app 冷启动重置——login_by_sms 对
        「停在其它页」无防护；重启后已登录落 tab_me（login_by_sms 早退）、
        未登录落登录页，两种态均可续行。

        到位判据按稳健度排序：
        1. 主：底部导航 4 图任一可见（已转正、跨机实测 1.0）；
        2. 辅：OCR「推荐」顶 Tab 文字；
        3. 兜底：顶 Tab 未选中态图轮询任一命中——首页 5 个顶 Tab 中至多
           1 个处于选中态，不依赖当前激活的是哪个顶 Tab（顶 Tab 持久化
           陷阱，见 knowledge/swan/pages/swan_首页.md）。

        底部播放条不再作到位门槛（verify-run3）：其模板截于「输出=扬声器/
        无曲目」态，rig 存在持久播放会话（输出=HiVi M300MKII+曲目名，
        服务端记忆，relaunch 不清）时播放条内容永久偏离模板；首页壳判据
        已由上述三级锚承担，播放条仅做非致命探测记日志。
        """
        if not (self._login_page_on_screen() or self._home_nav_visible()):
            logger.info("App 停在未知页（登录页/首页壳锚均不可见），冷启动重置")
            self.user.relaunch_app(os.environ.get("SWAN_PACKAGE", "com.swan.network"))
        self.user.login_by_sms(self.user.phone)
        self._wait_home_shell()
        if self.probe_image(SWAN_BOTTOM_PLAYER_BAR, timeout=2) is not None:
            logger.info("底部播放条可见（模板命中）")
        else:
            logger.warning(
                "底部播放条模板未命中（多为持久播放会话致动态内容偏离模板"
                "截图态），不作登录到位门槛")

    def _stay_on_recommend_tab(self) -> None:
        """把首页顶 Tab 停回「推荐」（顶 Tab 持久化陷阱）。

        未选中态图可见才点；已停在推荐时该图不匹配选中态，视为已到位。
        """
        if self.probe_image(SWAN_HOME_TAB_RECOMMEND, timeout=2) is not None:
            self.user.click_image(SWAN_HOME_TAB_RECOMMEND)
            self.user.image_exists(SWAN_HOME_TAB_MUSIC, timeout=10)

    def open_device_page(self) -> None:
        """首页 → 设备页。存量 key 迁移 2026-10-12：tab 点击改 [图]
        （SWAN_TAB_DEVICE 未选中态已转正图，verify 跨机实测 1.0）。

        幂等：已在设备页（右上角「添加设备」锚 [图] 可见）时短路不点——
        设备 Tab 已选中态其未选中态图不可见，直接 click_image 会超时（同
        go_bottom_tab 选中态口径；teardown 输出恢复路径可能停在设备页）。
        到位断言：右上角「添加设备」[图]（保留原口径）。
        """
        self.ensure_logged_in_on_home()
        if self.probe_image(SWAN_DEVICE_ADD_BTN, timeout=1) is not None:
            logger.info("_open_device_page: 已在设备页（添加设备锚 [图] 可见），短路返回")
            return
        self.user.click_image(SWAN_TAB_DEVICE, timeout=10)
        self.user.image_exists(SWAN_DEVICE_ADD_BTN, timeout=15)  # 右上角「添加设备」

    def open_player_page(self) -> None:
        """首页 → 点底部播放条进全屏播放页 → 断言顶栏渲染到位。

        主路径：底部播放条 [图] click_image——模板截于「输出=扬声器/无曲目」
        态，无播放会话时可用。

        兜底（verify-run3 实测）：rig 存在持久播放会话（服务端记忆，
        relaunch 不清）时播放条渲染「输出设备名+曲目名」（实测案例
        HiVi M300MKII+「多远都要在一起」），含动态内容区的模板永久失配。
        此时改在底部条带 region（_BOTTOM_BAR_REGION）内 OCR 定位点击——
        播放条必显示输出设备名或「- -」文字，OCR 定位对动态内容免疫；
        到位断言走 _wait_player_page_open（收起钮浅底/深底/旧单三模板，
        run5 脏跑实证单模板对电台播放页浅底失配——Radio Dum-Dum 亮黄
        背景下 9 条 wifi 用例全灭同因）。
        """
        self.ensure_logged_in_on_home()
        self.click_bottom_player_bar()
        self._wait_player_page_open(timeout=15)

    def click_bottom_player_bar(self) -> None:
        """点底部播放条：模板命中走 click_image，失配走条带 OCR 兜底。"""
        if self.probe_image(SWAN_BOTTOM_PLAYER_BAR, timeout=2) is not None:
            self.user.click_image(SWAN_BOTTOM_PLAYER_BAR, timeout=5)
            return
        logger.warning(
            "底部播放条模板未命中（持久播放会话致动态内容偏离模板截图态），"
            "转条带 OCR 兜底点击")
        items = [item for item in self.ocr_scan_page(region=self._BOTTOM_BAR_REGION)
                 if item["text"].strip()]
        assert items, "底部播放条 OCR 兜底失败：条带内未识别到任何文字（播放条未渲染？）"
        for item in items:
            # 取 OCR 文本前缀做二次定位探针：OCR 两次读数常有截断/空格差异，
            # 短前缀子串命中率最高；条带内全部文字均属播放条（区域已避开
            # 底部导航，无误点风险），任一命中即等效点中播放条
            probe = item["text"].strip()[:4]
            if self.user.find_text_by_ocr(probe, timeout=1,
                                        region=self._BOTTOM_BAR_REGION) is not None:
                logger.info("底部播放条 OCR 兜底命中: %r", probe)
                self.user.click_text(probe, timeout=2, region=self._BOTTOM_BAR_REGION)
                return
        assert False, (f"底部播放条 OCR 兜底点击失败: 条带文字 "
                       f"{[item['text'] for item in items]} 均未复现命中")

    # ---------- 播放前置 ----------

    def preset_playing(self, device_type: str, source: str = "favorite",
                        mode: str = "all") -> None:
        """播放前置（用例 13-28 共用）：确定输出设备 → 我喜欢页发起播放。

        device_type="speaker"：先校验当前输出为本机扬声器（_ensure_speaker_
        output，run4c 防污染——wifi_device 用例切换输出跨用例不回切，残留
        会让后续 speaker 用例起始态连红），再走默认输出，不做切换。

        device_type="wifi_device"：先在播放页弹层把输出切到 DEVICE_NAME
        （rig 音箱），并核对播放页顶部输出设备名已切换。⚠️ 输出已是目标时
        短路跳过弹层切换（run5 终账实测：rig 行已选中态重入弹层选行导航
        分叉，失败帧落设备页非播放页；进批时输出=rig 的场景有文件2 遗留
        与恢复脚本只暂停不切回两种来源）。

        source/mode 透传 start_play（A13）；发起前确保首页停在推荐顶 Tab。
        """
        self.ensure_logged_in_on_home()
        if device_type == "wifi_device":
            self.open_player_page()
            # run5 终账新签名：输出已=目标时重入弹层选行导航分叉（rig 行
            # 已选中态的点击行为未定义，失败帧 App 落设备页非播放页；进本
            # 批时输出已是 rig——文件2 遗留+恢复脚本只暂停不切回）——先探
            # 测页顶设备名已是目标则短路跳过弹层切换（方案①，实现最简）
            if self.user._wait_compact_text_in_region(
                    self.DEVICE_NAME, self._PLAYER_HEADER_DEVICE_REGION,
                    3.0, what="wifi 前置短路径探测", must=False):
                logger.info(
                    "wifi 前置：页顶输出设备名已是 %r，跳过弹层切换",
                    self.DEVICE_NAME)
            else:
                self.user.select_device(self.DEVICE_NAME, via="player")
                self._close_sheet_if_any()
            # 页顶输出设备名已切：compact 归一化轮询（与 select_device 收尾
            # 同口径——run6_clean2 实测 OCR 吞空格时裸 text_exists 子串永假，
            # 属构造性 flaky：今早保留空格 7/7 过、本轮吞空格 5/5 挂）
            self.user._wait_compact_text_in_region(
                self.DEVICE_NAME, self._PLAYER_HEADER_DEVICE_REGION, 10.0,
                what="切换输出后的播放页页顶设备名")
            self._dismiss_player_if_any()
        elif device_type == "speaker":
            self._ensure_speaker_output()
        else:
            raise ValueError(
                f"device_type 仅支持 speaker / wifi_device，收到 {device_type!r}")
        self._stay_on_recommend_tab()
        self.user.click_text("我喜欢", timeout=10)                   # 我喜欢卡片 [OCR]
        self.user.image_exists(SWAN_FAVORITE_PLAY_ALL, timeout=15)  # 已到我喜欢页
        self.user.start_play(source=source, mode=mode)

    def _restore_speaker_output_if_needed(self) -> None:
        """teardown 输出恢复（run5 对账新增，main 批准双保险）：输出非本机
        时经设备页切回「扬声器」。

        与 _preset_playing("speaker") 的 _ensure_speaker_output 前置校验
        互补：前置版在下场 speaker 用例开场兜底（硬断言），本版在每条用例
        收尾就把输出切回，根除「wifi 用例 → 后续 speaker 用例」的污染级联
        （run4c run2 / run5 run1 两轮实测同因）。状态判定与前置版同源：
        贴底播放条（_BOTTOM_BAR_REGION）OCR 读输出设备名——空/「- -」/含
        「扬声器」视为本机输出；其它（rig 会话残留）恢复。

        与前置版的差异：teardown 版**非断言**——恢复失败（select_device
        对 rig 电台活跃场景疑似不生效，run5 run1 实测 5 次恢复均无效，
        定责挂起待干净态复跑）只记 warning 不阻断收尾链，下场用例的前置
        恢复仍是第二道保险。此处 try/except 仅限清理动作，不掩盖任何
        用例断言（规则 6 口径）。
        """
        items = self.ocr_scan_page(region=self._BOTTOM_BAR_REGION)
        bar_text = "".join(item["text"] for item in items).strip()
        compact = bar_text.replace(" ", "")
        if not compact or "扬声器" in compact or set(compact) <= {"-", "."}:
            return
        logger.warning(
            "teardown 输出恢复：播放条输出设备 %r 非本机扬声器，经设备页切回",
            bar_text)
        try:
            self.open_device_page()
            self.user.select_device("扬声器", via="card")
            logger.info("teardown 输出恢复：已切回本机扬声器（select_device "
                        "本机分支含贴底条「扬声器」断言）")
        except AssertionError as exc:
            logger.warning(
                "teardown 输出恢复失败（不阻断收尾；下场 speaker 前置恢复"
                "仍会兜底）: %s", exc)

    def _ensure_speaker_output(self) -> None:
        """speaker 参数播放前置的输出防污染校验（run4c run2 实测新增）。

        wifi_device 参数用例把输出切到 rig 音箱后跨用例不自动回切
        （select_device 注记：切换真实下发且不回切），run2 中同批后续
        speaker 参数用例（test_volume_key[speaker-*] 等）起始态被污染连红
        8 条。本方法在播放发起前校验：首页贴底播放条（_BOTTOM_BAR_REGION）
        OCR 读输出设备名——播放条必显示输出设备名或「- -」（无会话）：
        - 含「扬声器」：本机输出，直接通过；
        - 为空或「- -」：无播放会话，默认本机输出，通过；
        - 其它设备名（rig 会话残留）：经设备页 select_device("扬声器")
          切回本机——新口径本机分支=点本机卡 → 系统电池优化弹窗点「忽略」
          → 设备页贴底播放条断言「扬声器」；切换失败（弹窗异常等）由
          select_device 内部断言显式报错，不静默吞掉。
        """
        items = self.ocr_scan_page(region=self._BOTTOM_BAR_REGION)
        bar_text = "".join(item["text"] for item in items).strip()
        compact = bar_text.replace(" ", "")
        if not compact or "扬声器" in compact or set(compact) <= {"-", "."}:
            return
        logger.warning(
            "speaker 前置：播放条输出设备 %r 非本机扬声器（前序 wifi 用例"
            "污染），经设备页 select_device 切回本机", bar_text)
        self.open_device_page()
        self.user.select_device("扬声器", via="card")
        # 切换收尾已由 select_device 本机分支断言（设备页贴底播放条
        # 「扬声器」）；后续 _stay_on_recommend_tab 经底部导航回首页。

    # ---------- 残留清理（G3/G4） ----------

    def _close_sheet_if_any(self) -> None:
        """设备弹层若还开着（标题行 [图] 可见）则返回键关闭。"""
        if self.probe_image(SWAN_DEVICE_SHEET_TITLE, timeout=1) is not None:
            self.user.press_back()

    def _close_volume_popup_if_any(self) -> None:
        """音量弹层若还开着（弹窗关闭钮锚 [图] 可见）则返回键关闭。

        verify-run4b：文件2 后半 wifi 用例「播放条点击后播放页打不开」疑似
        残留音量弹层诱因——前序用例 set_volume 收尾 press_back 偶发未关净
        （或物理音量键路径弹出的系统音量条），残留遮罩使下一次
        _open_player_page 点播放条落空。teardown 在关设备弹层后显式探测
        关闭（探测时播放页多半仍在前台，press_back 关弹层后即回播放页，
        与后续 _pause_if_playing/_dismiss_player_if_any 顺序衔接）。

        verify-run4c 复盘（run2/run3 实测）：旧整幅模板失配期临时降阈值
        0.5 探测存在假阳性——歌单详情页 0.55 / 播放页 0.58 / 首页 0.63-0.65
        误命中 → teardown 误 press_back（**首页按返回直接退 App**）→
        back_to_tab_shell 盲 back 连环放大，run3 5 条 teardown ERROR 同因。
        aw-element 已按 5.3.2 重截为弹窗右上角静态关闭钮锚（2026-09-28
        转正，开窗态实测 score=1.00，非弹窗页最高 0.65 区辨干净），恢复
        默认阈值 0.8。
        """
        if self.probe_image(SWAN_PLAYER_VOLUME_POPUP, timeout=1) is not None:
            logger.info("teardown: 音量弹层在位（关闭钮锚 [图]），press_back 关闭")
            self.user.press_back()

    def _pause_if_playing(self) -> None:
        """播放页可见且在播（⏸ [图]）时点暂停，避免 rig 音箱持续出声。

        仅覆盖播放页在前台的情形；后台播放（列表页迷你条）无独立模板可点，
        由后续用例的播放前置自然接管（rig 约定）。
        模板尚未入库（需授权平台+播放任务才能截）时 _probe_image 记日志
        跳过暂停检查，不炸 teardown（verify 首跑缺陷 1）。
        """
        if self.probe_image(SWAN_PLAYER_PAUSE_BTN, timeout=1) is not None:
            self.user.click_image(SWAN_PLAYER_PAUSE_BTN, timeout=2)

    def _dismiss_player_if_any(self) -> None:
        """全屏播放页若开着（收起钮 [图] 可见）则点收起回列表页。

        2026-09-28 起委托 SwanBusiness._dismiss_full_player 共用实现
        （run4c 复盘拍板）：收起钮浅底/深底双模板探测 + 顶栏 region 限定
        ——旧单模板对歌单详情页返回箭头 score 0.997 同形互扰为 teardown
        误点返回箭头根因，双模板极性实测 -0.9 根除；探测链含旧单模板与
        返回箭头态兜底（2026-09-29 追加，image_name_mapping.py 登记注记）。
        timeout=1 维持 teardown 快探测口径（播放页未开时四模板逐个失配，
        最坏约 4s）。
        """
        self._dismiss_full_player(timeout=1)

    def assert_on_login_page(self, timeout: float = 15.0) -> None:
        """登录页断言：登录页锚 [图]（置灰「下一步」/隐私政策链接任一）。"""
        assert self.user._login_page_anchor_visible(timeout=timeout), (
            "未回到登录页（登录页锚 [图] 未命中，请核对 SWAN_LOGIN_* 模板/页面改版）")
    def assert_on_home(self, timeout: float = 15.0) -> None:
        """首页断言：底部导航 4 图 [图] 任一轮询命中。

        底部播放条模板截于「输出=扬声器/- -」无会话态，rig 持久播放会话
        （输出=设备名+曲目名）下内容永久偏离模板，不作到位门槛，仅非致命
        探测记日志（口径同 swan_regression verify-run3）。
        """
        deadline = time.monotonic() + timeout
        while True:
            if any(self.probe_image(t, timeout=1) is not None
                   for t in self._BOTTOM_NAV_TEMPLATES):
                break
            if time.monotonic() >= deadline:
                assert False, (f"未进入首页（底部导航 4 图 [图] {timeout}s 均未命中，"
                               "请核对模板/是否停在其他页）")
            time.sleep(0.5)
        self.probe_bottom_player_bar()
    def assert_sms_form(self, timeout: float = 15.0) -> None:
        """验证码登录页形态互斥：[OCR]「密码登入」入口可见 + 密码框 [图] 不可见。

        入口用 OCR 而非图模板：「密码登入」灰胶囊图与密码页「验证码登入」
        钮同形互扰（文字子串滑动窗口假阳性，2026-10-13 实测 0.85），
        OCR 行文本"验证码登入"不含"密码登入"子串，天然区分。
        """
        assert self.user.find_text_by_ocr("密码登入", timeout=timeout) is not None, (
            "验证码登录形态断言失败（[OCR]「密码登入」入口未出现）")
        assert self.probe_image(SWAN_PASSWORD_FIELD, timeout=1) is None, (
            "验证码登录形态下出现了密码输入框 [图]，形态互斥被破坏")
    def assert_password_form(self, timeout: float = 15.0) -> None:
        """密码登录页形态判定：[OCR] 文案对比（"验证码登入"在 + "下一步"不在）。

        2026-10-13 终版口径——图模板在此页全面退役：①回切钮「验证码登入」
        有两态渲染（灰胶囊=空表单/黑字=填表后），单图判据必漏；②密码页黑底
        「登录」大按钮与验证码页置灰「下一步」模板形似误匹配（0.85 实测）。
        OCR 文案语义判定对两态渲染与形似干扰均免疫：密码页有「验证码登入」
        无「下一步」，验证码页反之。
        """
        assert self.user.find_text_by_ocr("验证码登入", timeout=timeout) is not None, (
            "密码登录形态断言失败（[OCR]「验证码登入」回切钮未出现）")
        assert self.user.find_text_by_ocr("下一步", timeout=1) is None, (
            "密码登录形态下仍存在「下一步」按钮 [OCR]，形态互斥被破坏")
    def ensure_fresh_sms_form(self) -> None:
        """前置归一化：确保停在全新验证码登录形态（空表单、协议未勾选）。

        - 已登录（底部导航 4 图任一可见）→ 先登出回登录页
        - 未登录但停在密码形态/脏表单 → 重启 App 重置（实测登录页表单
          无持久化，重启回到全新验证码形态）
        密码形态探测用双判据：SWAN_PASSWORD_FIELD [图]（空态）**或**
        [OCR]「验证码登入」（密码页特有回切钮文案，对掩码/已填残留态免疫
        ——2026-10-13 实测假表单掩码态空态图失配致探测漏判，单图判据废弃）。
        """
        if any(self.probe_image(t, timeout=1) is not None
               for t in self._BOTTOM_NAV_TEMPLATES):
            self.user.logout_if_needed()
        if (self.probe_image(SWAN_PASSWORD_FIELD, timeout=1) is not None
                or self.user.find_text_by_ocr("验证码登入", timeout=1) is not None):
            self.user.driver.stop_app(self.user.package)
            self.user.driver.start_app(self.user.package)
            assert self.user._login_page_anchor_visible(timeout=30), (
                "重启 App 后未回到登录页（登录页锚 [图] 未命中）")
        self.assert_sms_form()


    def assert_any_text(self, texts, timeout: int = 10) -> str:
        """OCR 断言任一文案出现，返回命中的文案（用于同一区域的文案变体）。"""
        for text in texts:
            if self.user.find_text_by_ocr(text, timeout=1) is not None:
                return text
        assert False, f"OCR 均未找到任一文案: {list(texts)}"

    def probe_bottom_player_bar(self, timeout: int = 2) -> None:
        """底部播放条非致命探测：模板命中记 info，未命中记 warning 不挂。

        模板截于「输出=扬声器/- -」无会话态；rig 存在持久播放会话
        （输出=HiVi M300MKII+曲目名，relaunch 不清）时播放条内容永久偏离
        模板，不作断言门槛（verify-run3 口径）。
        """
        if self.probe_image(SWAN_BOTTOM_PLAYER_BAR, timeout=timeout) is not None:
            logger.info("底部播放条可见（模板命中）")
        else:
            logger.warning(
                "底部播放条模板未命中（多为持久播放会话致动态内容偏离模板"
                "截图态），不作断言门槛")

    def assert_home_shell_image(self, timeout: int = 3) -> None:
        """首页壳图片级确认：底部导航 4 图任一可见（已转正、跨机稳健 1.0）。"""
        for template in self._BOTTOM_NAV_TEMPLATES:
            if self.probe_image(template, timeout=timeout) is not None:
                return
        assert False, "首页壳图片确认失败：底部导航 4 图（首页/平台/设备/我的）均未命中"
class SwanLoginRegressionMixin:
    """登录域存量用例 mixin（登录/登出、密码登录、只读页三域共用断言与探测辅助）。

    2026-10-12 一用例一文件拆分时从 test_swan_login_logout.py /
    test_swan_password_login.py / test_swan_readonly_pages.py 的三份复制
    粘贴副本抽出。⚠️ 本组用例为存量 key 定位实现（断言走
    wait_accessibility / accessibility_exists），属「存量 key 迁移待拍板」
    范围（docs/待办与缺口清单.md「定位策略定稿」节），迁移前保持原口径，
    新用例不要模仿（CLAUDE.md 规则 2）。
    """

    # ---------- 断言辅助（2026-10-12 登录域 key 迁移：全 [图]/[OCR]） ----------






    def ensure_logged_in_on_home(self) -> None:
        """幂等登录并断言在首页（登录域口径：底部导航 4 图 [图] 任一轮询命中）。

        ⚠️ 与 SwanPlayerRegressionMixin._ensure_logged_in_on_home（图片三级
        锚判据）同名不同实现：本版为登录域简版（4 图壳锚，无顶 Tab 轮询），
        仅登录域用例使用。
        底部播放条模板截于「输出=扬声器/- -」无会话态，rig 持久播放会话
        （输出=设备名+曲目名）下内容永久偏离模板，不作到位门槛，仅非致命
        探测记日志（口径同 swan_regression verify-run3）。
        """
        self.user.login_by_sms(self.user.phone)
        deadline = time.monotonic() + 15
        while True:
            if any(self.probe_image(t, timeout=1) is not None
                   for t in self._BOTTOM_NAV_TEMPLATES):
                break
            if time.monotonic() >= deadline:
                assert False, "未进入首页（底部导航 4 图 [图] 15s 均未命中）"
            time.sleep(0.5)
        self.probe_bottom_player_bar()


    # ---------- 锚点探测辅助（口径同 swan_regression） ----------


    def probe_image(self, template: str, timeout: int = 1):
        """模板文件在盘才 find_image；缺失记日志按未命中处理。

        AWBase.find_image 对缺失模板文件是 assert 崩溃而非返回 None，
        探测类「可选命中」调用先 os.path.exists 防护（常量为绝对路径）。
        """
        if not os.path.exists(template):
            logger.warning("模板图未入库，按未命中跳过: %s", template)
            return None
        return self.user.find_image(template, timeout=timeout)




class SwanContentRegressionMixin(SwanPlayerRegressionMixin):
    """导航/收藏历史/搜索域回归用例 mixin：push 页反向退出式清理。"""

    FAVORITE_PLATFORMS = [p.strip() for p in
                          os.environ.get("SWAN_FAV_PLATFORMS", "swan").split(",")
                          if p.strip()]
    COLLECT_PLATFORMS = [p.strip() for p in
                         os.environ.get("SWAN_COLLECT_PLATFORMS", "swan").split(",")
                         if p.strip()]
    COLLECT_PLAYLIST = os.environ.get("SWAN_COLLECT_PLAYLIST", "我的音乐")
    # source="player" 分支收藏曲：显式配置优先，回落 SWAN_TEST_SONG（rig
    # 我喜欢页已验证可达的歌名，见 start_play mode="song" 注）——二者皆空
    # 时 collect_song[player] 走播放全部首曲（无预清理遗留分支，见
    # test_collect_song 注）
    COLLECT_PLAYER_SONG = (os.environ.get("SWAN_COLLECT_PLAYER_SONG", "").strip()
                           or os.environ.get("SWAN_TEST_SONG", "").strip())

    def preset_playing_on_favorite(self, source: str = "favorite",
                                    mode: str = "all") -> None:
        """播放前置（本批用例）：推荐顶 Tab -> 我喜欢卡 [OCR] -> 发起播放。

        与播放器域 _preset_playing("speaker") 的差别仅在到位断言：按任务
        约束改用 OCR 页面判据「宝藏音乐，随心收藏」（我喜欢页特有，知识库
        生效断言），不复用含"0首歌"计数的 SWAN_FAVORITE_PLAY_ALL 模板
        （歌单加歌后失配，见 image/image_name_mapping.py 注记）。
        播放发起仍复用域3 start_play（不重写播放逻辑）。
        """
        self.ensure_logged_in_on_home()
        self._stay_on_recommend_tab()
        self.user.click_text("我喜欢", timeout=10)                  # 我喜欢卡片 [OCR]
        self.user.text_exists("宝藏音乐，随心收藏", timeout=15)     # 我喜欢页判据 [OCR]
        self.user.start_play(source=source, mode=mode)


