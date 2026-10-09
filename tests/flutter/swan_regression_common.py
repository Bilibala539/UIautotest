"""Swan 回归·播放器域公共前置与清理（test_播放器*.py 三个用例文件共用）。

非用例模块（无 test_ 前缀，pytest 与 run_parallel 均不收集）。
新代码定位一律图像模板 > OCR 文本（方案 §0）；唯一例外是 tab_device 的
存量 key 导航（迁移待拍板，见 docs/待办与缺口清单.md「定位策略定稿」节）。

rig 环境变量：
- SWAN_DEVICE_NAME  rig WiFi 音箱设备名（默认 Libretto_0E00，知识库实测绑定设备）
- SWAN_TEST_SONG    我喜欢歌单中的歌曲名（用例14 单曲播放；未配置则 skip）
"""
from __future__ import annotations

import logging
import os

from image.image_name_mapping import (
    SWAN_BOTTOM_PLAYER_BAR,
    SWAN_DEVICE_ADD_BTN,
    SWAN_DEVICE_SHEET_TITLE,
    SWAN_FAVORITE_PLAY_ALL,
    SWAN_HOME_TAB_AI,
    SWAN_HOME_TAB_MUSIC,
    SWAN_HOME_TAB_RADIO,
    SWAN_HOME_TAB_RECOMMEND,
    SWAN_LOGIN_PRIVACY_POLICY_LINK,
    SWAN_LOGIN_SUBMIT_BTN,
    SWAN_PLAYER_DISMISS_BTN,
    SWAN_PLAYER_PAUSE_BTN,
    SWAN_TAB_DEVICE,
    SWAN_TAB_HOME,
    SWAN_TAB_ME,
    SWAN_TAB_PLATFORM,
)
from utils.aw.business.swan import SwanBusiness

logger = logging.getLogger(__name__)

DEVICE_TYPES = ["speaker", "wifi_device"]  # speaker=手机扬声器默认输出 / wifi_device=rig 音箱


class SwanPlayerRegressionMixin:
    """播放器域回归用例 mixin：登录/导航/播放前置与 G3/G4 清理。

    与 BaseTest 一起继承（mixin 放前），setup/teardown 由 conftest 的
    _auto_test_lifecycle 自动调用。
    """

    DEVICE_NAME = os.environ.get("SWAN_DEVICE_NAME", "Libretto_0E00")
    SONG_NAME = os.environ.get("SWAN_TEST_SONG", "")

    user = None
    aw = None
    phone = ""

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

    def setup(self):
        self.user = self.users("swan")
        self.aw = self.user.aw  # 业务层实例 = 基础操作 + SwanBusiness 业务方法
        self.phone = self.user.phone

    def teardown(self):
        """G3/G4：关残留弹层 → 尽力暂停（rig 卫生）→ 收播放页 → 回首页。"""
        self._close_sheet_if_any()
        self._pause_if_playing()
        self._dismiss_player_if_any()
        self.user.go_home()

    # ---------- 锚点探测（模板缺失防护 + 首页壳判据） ----------

    def _probe_image(self, template: str, timeout: int = 1):
        """模板文件在盘才 find_image；缺失记日志按未命中处理。

        AWBase.find_image 对缺失模板文件是 assert 崩溃而非返回 None（框架层
        行为，已单独上报），清理/锚点探测这类「可选命中」调用先 os.path.exists
        防护（常量为绝对路径），避免模板未入库（如 SWAN_PLAYER_PAUSE_BTN，
        需授权平台+播放任务才能截）时炸掉 teardown。
        """
        if not os.path.exists(template):
            logger.warning("模板图未入库，按未命中跳过: %s", template)
            return None
        return self.aw.find_image(template, timeout=timeout)

    def _login_page_on_screen(self, timeout: int = 1) -> bool:
        """登录页锚：「下一步」按钮 / 隐私政策链接图任一可见。"""
        return any(self._probe_image(template, timeout=timeout) is not None
                   for template in self._LOGIN_PAGE_TEMPLATES)

    def _home_nav_visible(self, timeout: int = 1) -> bool:
        """首页壳主锚：底部导航 4 图任一可见（已转正、跨机稳健，verify 实测 1.0）。"""
        return any(self._probe_image(template, timeout=timeout) is not None
                   for template in self._BOTTOM_NAV_TEMPLATES)

    def _wait_home_shell(self) -> None:
        """断言已到首页壳：主底部导航 4 图 → 辅 OCR「推荐」→ 兜底顶 Tab 图。"""
        if self._home_nav_visible(timeout=3):
            return
        if self.aw.find_text_by_ocr("推荐", timeout=3) is not None:
            return
        for template in self._TOP_TAB_TEMPLATES:
            if self._probe_image(template, timeout=2) is not None:
                return
        assert False, "未进入首页壳（底部导航 4 图 / OCR「推荐」/ 顶 Tab 未选中态图均未命中）"

    # ---------- 登录与导航 ----------

    def _ensure_logged_in_on_home(self) -> None:
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
        self.user.login_by_sms(self.phone)
        self._wait_home_shell()
        if self._probe_image(SWAN_BOTTOM_PLAYER_BAR, timeout=2) is not None:
            logger.info("底部播放条可见（模板命中）")
        else:
            logger.warning(
                "底部播放条模板未命中（多为持久播放会话致动态内容偏离模板"
                "截图态），不作登录到位门槛")

    def _stay_on_recommend_tab(self) -> None:
        """把首页顶 Tab 停回「推荐」（顶 Tab 持久化陷阱）。

        未选中态图可见才点；已停在推荐时该图不匹配选中态，视为已到位。
        """
        if self._probe_image(SWAN_HOME_TAB_RECOMMEND, timeout=2) is not None:
            self.aw.click_image(SWAN_HOME_TAB_RECOMMEND)
            self.aw.image_exists(SWAN_HOME_TAB_MUSIC, timeout=10)

    def _open_device_page(self) -> None:
        """首页 → 设备页。tab 点击为存量 key 导航（迁移待拍板），到位断言用已转正图片。"""
        self._ensure_logged_in_on_home()
        self.aw.click_accessibility(SwanBusiness.KEY_TAB_DEVICE)
        self.aw.image_exists(SWAN_DEVICE_ADD_BTN, timeout=15)  # 右上角「添加设备」

    def _open_player_page(self) -> None:
        """首页 → 点底部播放条进全屏播放页 → 断言顶栏渲染 [图]。

        主路径：底部播放条 [图] click_image——模板截于「输出=扬声器/无曲目」
        态，无播放会话时可用。

        兜底（verify-run3 实测）：rig 存在持久播放会话（服务端记忆，
        relaunch 不清）时播放条渲染「输出设备名+曲目名」（实测案例
        HiVi M300MKII+「多远都要在一起」），含动态内容区的模板永久失配。
        此时改在底部条带 region（_BOTTOM_BAR_REGION）内 OCR 定位点击——
        播放条必显示输出设备名或「- -」文字，OCR 定位对动态内容免疫；
        到位仍以播放页收起钮 [图] 硬断言收口。
        """
        self._ensure_logged_in_on_home()
        self._click_bottom_player_bar()
        self.aw.image_exists(SWAN_PLAYER_DISMISS_BTN, timeout=15)

    def _click_bottom_player_bar(self) -> None:
        """点底部播放条：模板命中走 click_image，失配走条带 OCR 兜底。"""
        if self._probe_image(SWAN_BOTTOM_PLAYER_BAR, timeout=2) is not None:
            self.aw.click_image(SWAN_BOTTOM_PLAYER_BAR, timeout=5)
            return
        logger.warning(
            "底部播放条模板未命中（持久播放会话致动态内容偏离模板截图态），"
            "转条带 OCR 兜底点击")
        items = [item for item in self.aw.ocr_scan_page(region=self._BOTTOM_BAR_REGION)
                 if item["text"].strip()]
        assert items, "底部播放条 OCR 兜底失败：条带内未识别到任何文字（播放条未渲染？）"
        for item in items:
            # 取 OCR 文本前缀做二次定位探针：OCR 两次读数常有截断/空格差异，
            # 短前缀子串命中率最高；条带内全部文字均属播放条（区域已避开
            # 底部导航，无误点风险），任一命中即等效点中播放条
            probe = item["text"].strip()[:4]
            if self.aw.find_text_by_ocr(probe, timeout=1,
                                        region=self._BOTTOM_BAR_REGION) is not None:
                logger.info("底部播放条 OCR 兜底命中: %r", probe)
                self.aw.click_text(probe, timeout=2, region=self._BOTTOM_BAR_REGION)
                return
        assert False, (f"底部播放条 OCR 兜底点击失败: 条带文字 "
                       f"{[item['text'] for item in items]} 均未复现命中")

    # ---------- 播放前置 ----------

    def _preset_playing(self, device_type: str, source: str = "favorite",
                        mode: str = "all") -> None:
        """播放前置（用例 13-28 共用）：确定输出设备 → 我喜欢页发起播放。

        device_type="speaker"：使用默认输出（手机扬声器），不做切换——
        无任务态设备弹层中当前设备行无勾选圆点（知识库实测），无法用勾选态
        图断言"切回本机"，故约定该参数用例须在输出=手机扬声器的起始态执行
        （同文件内 speaker 参数先于 wifi_device 收集执行）。

        device_type="wifi_device"：先在播放页弹层把输出切到 DEVICE_NAME
        （rig 音箱），并核对播放页顶部输出设备名已切换。

        source/mode 透传 start_play（A13）；发起前确保首页停在推荐顶 Tab。
        """
        self._ensure_logged_in_on_home()
        if device_type == "wifi_device":
            self._open_player_page()
            self.user.select_device(self.DEVICE_NAME, via="player")
            self._close_sheet_if_any()
            self.aw.text_exists(self.DEVICE_NAME, timeout=10)  # 页顶输出设备名已切
            self._dismiss_player_if_any()
        elif device_type != "speaker":
            raise ValueError(
                f"device_type 仅支持 speaker / wifi_device，收到 {device_type!r}")
        self._stay_on_recommend_tab()
        self.aw.click_text("我喜欢", timeout=10)                   # 我喜欢卡片 [OCR]
        self.aw.image_exists(SWAN_FAVORITE_PLAY_ALL, timeout=15)  # 已到我喜欢页
        self.user.start_play(source=source, mode=mode)

    # ---------- 残留清理（G3/G4） ----------

    def _close_sheet_if_any(self) -> None:
        """设备弹层若还开着（标题行 [图] 可见）则返回键关闭。"""
        if self._probe_image(SWAN_DEVICE_SHEET_TITLE, timeout=1) is not None:
            self.aw.press_back()

    def _pause_if_playing(self) -> None:
        """播放页可见且在播（⏸ [图]）时点暂停，避免 rig 音箱持续出声。

        仅覆盖播放页在前台的情形；后台播放（列表页迷你条）无独立模板可点，
        由后续用例的播放前置自然接管（rig 约定）。
        模板尚未入库（需授权平台+播放任务才能截）时 _probe_image 记日志
        跳过暂停检查，不炸 teardown（verify 首跑缺陷 1）。
        """
        if self._probe_image(SWAN_PLAYER_PAUSE_BTN, timeout=1) is not None:
            self.aw.click_image(SWAN_PLAYER_PAUSE_BTN, timeout=2)

    def _dismiss_player_if_any(self) -> None:
        """全屏播放页若开着（收起钮 [图] 可见）则点收起回列表页。"""
        if self._probe_image(SWAN_PLAYER_DISMISS_BTN, timeout=1) is not None:
            self.aw.click_image(SWAN_PLAYER_DISMISS_BTN, timeout=5)
