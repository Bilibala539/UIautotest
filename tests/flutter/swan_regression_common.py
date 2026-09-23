"""Swan 回归·播放器域公共前置与清理（test_播放器*.py 三个用例文件共用）。

非用例模块（无 test_ 前缀，pytest 与 run_parallel 均不收集）。
新代码定位一律图像模板 > OCR 文本（方案 §0）；唯一例外是 tab_device 的
存量 key 导航（迁移待拍板，见 docs/待办与缺口清单.md「定位策略定稿」节）。

rig 环境变量：
- SWAN_DEVICE_NAME  rig WiFi 音箱设备名（默认 Libretto_0E00，知识库实测绑定设备）
- SWAN_TEST_SONG    我喜欢歌单中的歌曲名（用例14 单曲播放；未配置则 skip）
"""
from __future__ import annotations

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
    SWAN_PLAYER_DISMISS_BTN,
    SWAN_PLAYER_PAUSE_BTN,
)
from utils.aw.business.swan import SwanBusiness

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

    # ---------- 登录与导航 ----------

    def _ensure_logged_in_on_home(self) -> None:
        """幂等登录并断言在首页（登录复用存量 login_by_sms；到位断言用图片）。

        顶 Tab 断言用「未选中态」图轮询任一命中：首页 5 个顶 Tab 中至多
        1 个处于选中态，任一张未选中态图可见即在首页，不依赖当前激活的是
        哪个顶 Tab（顶 Tab 持久化陷阱，见 knowledge/swan/pages/swan_首页.md）。
        """
        self.user.login_by_sms(self.phone)
        for template in (SWAN_HOME_TAB_RECOMMEND, SWAN_HOME_TAB_MUSIC,
                         SWAN_HOME_TAB_RADIO, SWAN_HOME_TAB_AI):
            if self.aw.find_image(template, timeout=2) is not None:
                break
        else:
            assert False, "首页顶 Tab 未渲染（4 张未选中态图均未匹配）"
        self.aw.image_exists(SWAN_BOTTOM_PLAYER_BAR, timeout=10)

    def _stay_on_recommend_tab(self) -> None:
        """把首页顶 Tab 停回「推荐」（顶 Tab 持久化陷阱）。

        未选中态图可见才点；已停在推荐时该图不匹配选中态，视为已到位。
        """
        if self.aw.find_image(SWAN_HOME_TAB_RECOMMEND, timeout=2) is not None:
            self.aw.click_image(SWAN_HOME_TAB_RECOMMEND)
            self.aw.image_exists(SWAN_HOME_TAB_MUSIC, timeout=10)

    def _open_device_page(self) -> None:
        """首页 → 设备页。tab 点击为存量 key 导航（迁移待拍板），到位断言用已转正图片。"""
        self._ensure_logged_in_on_home()
        self.aw.click_accessibility(SwanBusiness.KEY_TAB_DEVICE)
        self.aw.image_exists(SWAN_DEVICE_ADD_BTN, timeout=15)  # 右上角「添加设备」

    def _open_player_page(self) -> None:
        """首页 → 点底部播放条 [图] 进全屏播放页 → 断言顶栏渲染 [图]。

        ⚠️ 底部播放条模板含曲目名区（映射文件已注明），后台残留播放会使其
        失配；用例序列依赖 teardown 的 _pause_if_playing 控制该残留。
        """
        self._ensure_logged_in_on_home()
        self.aw.click_image(SWAN_BOTTOM_PLAYER_BAR, timeout=10)
        self.aw.image_exists(SWAN_PLAYER_DISMISS_BTN, timeout=15)

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
        if self.aw.find_image(SWAN_DEVICE_SHEET_TITLE, timeout=1) is not None:
            self.aw.press_back()

    def _pause_if_playing(self) -> None:
        """播放页可见且在播（⏸ [图]）时点暂停，避免 rig 音箱持续出声。

        仅覆盖播放页在前台的情形；后台播放（列表页迷你条）无独立模板可点，
        由后续用例的播放前置自然接管（rig 约定）。
        """
        if self.aw.find_image(SWAN_PLAYER_PAUSE_BTN, timeout=1) is not None:
            self.aw.click_image(SWAN_PLAYER_PAUSE_BTN, timeout=2)

    def _dismiss_player_if_any(self) -> None:
        """全屏播放页若开着（收起钮 [图] 可见）则点收起回列表页。"""
        if self.aw.find_image(SWAN_PLAYER_DISMISS_BTN, timeout=1) is not None:
            self.aw.click_image(SWAN_PLAYER_DISMISS_BTN, timeout=5)
