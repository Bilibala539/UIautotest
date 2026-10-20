"""Swan 回归 P04（播放器）包级业务 mixin —— SwanRP04Mixin。

tcbatch P04 批次（player-NEG/POS 文字用例批转）新增方法沉淀；纯 mixin 不继承，
由集成方挂入 SwanBusiness MRO 后生效（挂入前 userA 静态视图与运行时代理均不可见）。
调用约定与 swan_regression.py 一致：
- 基础 AW 方法经 self.<方法>（aw_base / flutter_base / android_base）；
- 既有业务方法（含私有辅助）经 self.user.<方法>（user 对象 __getattr__ 代理回业务层）。
"""

from __future__ import annotations

import logging
import os
import time

from image.image_name_mapping import (
    SWAN_DEVICE_SHEET_TITLE,
    SWAN_PLAYER_VOLUME_POPUP,
)

logger = logging.getLogger(__name__)


class SwanRP04Mixin:
    """P04 播放器域新增业务方法（重启 / 播放页读态 / 弹层与底栏编排）。"""

    # 播放页曲目区（歌名/歌手行）OCR band：页头设备名带 (0,60,720,120) 之下、
    # 封面之上；曲目为动态元素无图像模板（知识库口径），一律 OCR 读取。
    _P04_PLAYER_TITLE_BAND = (0, 180, 720, 180)

    # 底栏迷你播放条 band（与 swan_regression._BOTTOM_BAR_REGION 同源口径，
    # 4 tab 导航标签在该 band 之下不计入）。
    _P04_BOTTOM_BAR_REGION = (0, 1370, 720, 116)

    def restart_app(self, timeout: float = 30.0) -> None:
        """杀进程冷重启 App 并落首页（NEG-006/NEG-034/POS-036 重启类用例复用）。

        package 取环境变量 SWAN_PACKAGE（缺省 com.swan.network），与
        relaunch_app / cold_start_assert 同源；relaunch_app 内置首页锚断言，
        播放会话经持久化在重启后由 App 自动恢复（rig 实测 relaunch 不清会话）。
        """
        self.user.relaunch_app(
            os.environ.get("SWAN_PACKAGE", "com.swan.network"), timeout=timeout)

    def rig_device_name(self) -> str:
        """rig WiFi 音箱设备名（环境变量 SWAN_DEVICE_NAME，缺省 Libretto_0E00）。

        与 SwanPlayerRegressionMixin.DEVICE_NAME 同源；用例层经本方法取值
        内联进 select_device 等调用的实参。
        """
        return os.environ.get("SWAN_DEVICE_NAME", "Libretto_0E00")

    def read_player_title(self, timeout: float = 10.0) -> str | None:
        """OCR 读取播放页歌名（曲目区 band 最上一行文本），读不到返回 None。

        POS-005 身份区非空 / POS-018 启动期渲染 / POS-019 切歌换曲复用；
        歌名随曲目动态变化不做精确匹配，由调用方断言（非空 / 变化 / 包含）。
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            items = [i for i in self.ocr_scan_page(region=self._P04_PLAYER_TITLE_BAND)
                     if i.get("text", "").strip()]
            if items:
                title = min(items, key=lambda i: i["cy"])["text"].strip()
                logger.info(f"✅ read_player_title 成功：{title!r}")
                return title
            self.sleep(0.5)
        logger.error("❌ read_player_title 失败：曲目区 band 无 OCR 文本")
        return None

    def read_player_progress(self, timeout: float = 8.0) -> tuple[int, int] | None:
        """OCR 读取播放进度双时间，返回 (已播秒, 总秒)，读不到返回 None。

        POS-018/POS-021/NEG-030 复用；为 swan.py._ocr_progress_times 的
        公开转发（用例层不直调私有辅助）。
        """
        return self.user._ocr_progress_times(timeout=timeout)

    def open_volume_popup(self) -> None:
        """播放页打开音量弹层并断言弹层锚（不改动音量值）。

        NEG-008/POS-039 复用：音量图标模板链（浅底/深底/基础三态）探测命中
        后点击，弹层锚 [图] 断言收尾；关闭由调用方 press_back 后复探。
        """
        template = self.user._find_volume_icon(timeout=5)
        assert template is not None, (
            "播放页未探测到音量图标（浅底/深底/基础三模板均未命中）")
        self.user.click_image(template, timeout=5)
        assert self.user.find_image(SWAN_PLAYER_VOLUME_POPUP, timeout=5) is not None, (
            "音量弹层锚 [图] 未命中：弹层未弹出或锚失配")
        logger.info("✅ open_volume_popup 成功")

    def close_full_player(self, timeout: float = 5.0) -> None:
        """收起全屏播放页回列表页（收起钮模板链点击，非盲 back）。

        POS-002 复用：收起钮为浅底/深底/旧单/返回箭头四态模板链 + 顶栏
        region 限定（同形互扰双保险），为 swan.py._dismiss_full_player 的
        公开转发（用例层不直调私有辅助）。
        """
        self.user._dismiss_full_player(timeout=timeout)

    def open_queue_sheet(self) -> None:
        """播放页打开播放队列弹层（B 标定项：队列按钮与弹层锚模板均待注册）。

        队列按钮为无文案图标（知识库 player_queue_button「待截/草稿」），
        OCR 无文本锚——先按 OCR 候选词尽力定位点击，全部未命中即断言失败
        并指明待注册模板（package_report.template_needs：队列按钮/队列弹层
        锚）。⚠️ 须有播放任务前置（无任务时点击无任何反应，知识库实测）。
        """
        self.user._wait_player_page_open(timeout=10)
        for candidate in ("队列", "播放队列", "当前播放"):
            if self.user.find_text_by_ocr(candidate, timeout=2) is not None:
                self.user.click_text(candidate, timeout=3)
                return
        assert False, (
            "队列按钮无 OCR 文本锚且图像模板未注册（SWAN_PLAYER_QUEUE_BTN "
            "待截取，见 package_report.template_needs；队列弹层锚同待注册）")

    def start_external_app(self, package: str) -> None:
        """拉起设备上第三方 App（音频焦点抢占类用例）。NEG-026 复用。

        经平台驱动 start_app（与 swan.py cold_start_assert/background_resume
        同一 driver 通道）；包名由用例经环境变量注入（真机预置项）。
        """
        self.driver.start_app(package)

    def stop_external_app(self, package: str) -> None:
        """停止设备上第三方 App（音频焦点归还）。NEG-026 复用。"""
        self.driver.stop_app(package)

    def open_device_sheet(self) -> None:
        """播放页打开输出设备弹层并断言弹层标题锚。

        POS-030 复用：设备按钮模板链（基础/字形/绿色三态）探测命中后点击，
        弹层标题 [图] 断言收尾；关闭由调用方 press_back。
        """
        template = self.user._find_device_btn(timeout=5)
        assert template is not None, (
            "播放页未探测到设备按钮（基础/字形/绿色三模板均未命中）")
        self.user.click_image(template, timeout=5)
        assert self.user.find_image(SWAN_DEVICE_SHEET_TITLE, timeout=5) is not None, (
            "设备弹层标题锚 [图] 未命中：弹层未打开或锚失配")
        logger.info("✅ open_device_sheet 成功")

    def assert_bottom_bar_session(self, visible: bool, device: str = "扬声器",
                                  timeout: float = 6.0) -> None:
        """断言底栏迷你播放条会话显隐（band 内输出设备名签名行在/不在）。

        POS-002/POS-036 复用。签名行=输出设备名：本机会话传缺省「扬声器」
        （与 _ensure_speaker_output 判定同源），rig 会话传 rig 设备名
        （rig_device_name()）。全屏播放页打开时条带按契约隐藏，band 仅剩
        页面自身文本（音量行/进度行），无设备名行。比对两侧去空格小写
        归一（rig 型号名 OCR 存在 l/I 同形失真，仅保主干可辨）。
        """
        deadline = time.monotonic() + timeout
        found = False
        texts: list[str] = []
        needle = device.replace(" ", "").lower()
        while True:
            texts = [i["text"] for i in
                     self.ocr_scan_page(region=self._P04_BOTTOM_BAR_REGION)]
            found = any(needle in t.replace(" ", "").lower() for t in texts)
            if found == visible:
                return
            if time.monotonic() >= deadline:
                break
            self.sleep(0.5)
        expect = "可见" if visible else "隐藏"
        actual = "见签名行" if found else "未见签名行"
        assert False, (
            f"底栏迷你播放条显隐不符：期望{expect}，实际{actual}"
            f"（签名={device!r}，band OCR {texts}）")
