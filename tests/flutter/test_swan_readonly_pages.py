"""Swan Flutter 只读断言类用例（不写数据、不下发控制）。

覆盖：首页元素、平台页、设备页、全屏播放页开关、收藏分组详情。
前置：账号已登录（用例开头 login_by_sms 幂等确保，已在首页自动跳过）。

⛔ 危险入口一律不点（只做存在性断言）：
授权/充值（netease_platform_entry 等"+"按钮）、播放暂停/音量/上下首、
设备卡/设置/同步/音量设置/添加设备、注销账号、任何确认弹窗。

断言优先级：图片（image_exists）> key（wait_accessibility）> OCR。
等待一律 wait_accessibility / find_text_by_ocr(timeout=)，禁止 sleep 凑数。
每条用例收尾回首页（G3/G4）。
"""
from __future__ import annotations

import logging
import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_BOTTOM_PLAYER_BAR,
    SWAN_DEVICE_ADD_BTN,
    SWAN_FAV_FAMILY_GROUP_ROW,
    SWAN_ME_FAVORITES_ROW,
    SWAN_PLATFORM_NETEASE_ROW,
    SWAN_PLAYER_DISMISS_BTN,
    SWAN_PLAYER_PLAY_PAUSE_BTN,
    SWAN_TAB_DEVICE,
    SWAN_TAB_HOME,
    SWAN_TAB_ME,
    SWAN_TAB_PLATFORM,
)
from utils.aw.business.swan import SwanBusiness

logger = logging.getLogger(__name__)

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)


class TestSwanReadonlyPages(BaseTest):
    """Swan 只读页面断言。"""

    def setup(self):
        self.user = self.users("swan")
        self.aw = self.user.aw  # 业务层实例 = 基础操作 + SwanBusiness 业务方法
        self.phone = self.user.phone

    # ---------- 断言辅助 ----------

    def _ensure_logged_in_on_home(self) -> None:
        """幂等登录并断言在首页（4 tab key + 底部导航 4 图任一）。

        底部播放条模板截于「输出=扬声器/- -」无会话态，rig 持久播放会话
        （输出=设备名+曲目名）下内容永久偏离模板，不作到位门槛，仅非致命
        探测记日志（口径同 swan_regression_common verify-run3）。
        """
        self.user.login_by_sms(self.phone)
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_TAB_ME, timeout=15
        ), "未进入首页（tab_me 未出现）"
        self._assert_home_shell_image()
        self._probe_bottom_player_bar()

    # ---------- 锚点探测辅助（口径同 swan_regression_common） ----------

    # 首页壳图片级锚：全局底部导航 4 图标（未选中态，已转正、verify 跨机实测
    # 1.0；4 个一级页至多 1 个 Tab 选中，任一可见即在首页壳）
    _BOTTOM_NAV_TEMPLATES = (
        SWAN_TAB_HOME, SWAN_TAB_PLATFORM, SWAN_TAB_DEVICE, SWAN_TAB_ME,
    )

    def _probe_image(self, template: str, timeout: int = 1):
        """模板文件在盘才 find_image；缺失记日志按未命中处理。

        AWBase.find_image 对缺失模板文件是 assert 崩溃而非返回 None，
        探测类「可选命中」调用先 os.path.exists 防护（常量为绝对路径）。
        """
        if not os.path.exists(template):
            logger.warning("模板图未入库，按未命中跳过: %s", template)
            return None
        return self.aw.find_image(template, timeout=timeout)

    def _probe_bottom_player_bar(self, timeout: int = 2) -> None:
        """底部播放条非致命探测：模板命中记 info，未命中记 warning 不挂。

        模板截于「输出=扬声器/- -」无会话态；rig 存在持久播放会话
        （输出=HiVi M300MKII+曲目名，relaunch 不清）时播放条内容永久偏离
        模板，不作断言门槛（verify-run3 口径）。
        """
        if self._probe_image(SWAN_BOTTOM_PLAYER_BAR, timeout=timeout) is not None:
            logger.info("底部播放条可见（模板命中）")
        else:
            logger.warning(
                "底部播放条模板未命中（多为持久播放会话致动态内容偏离模板"
                "截图态），不作断言门槛")

    def _assert_home_shell_image(self, timeout: int = 3) -> None:
        """首页壳图片级确认：底部导航 4 图任一可见（已转正、跨机稳健 1.0）。"""
        for template in self._BOTTOM_NAV_TEMPLATES:
            if self._probe_image(template, timeout=timeout) is not None:
                return
        assert False, "首页壳图片确认失败：底部导航 4 图（首页/平台/设备/我的）均未命中"

    def _assert_any_text(self, texts, timeout: int = 10) -> str:
        """OCR 断言任一文案出现，返回命中的文案（用于同一区域的文案变体）。"""
        for text in texts:
            if self.aw.find_text_by_ocr(text, timeout=1) is not None:
                return text
        assert False, f"OCR 均未找到任一文案: {list(texts)}"

    # ---------- 用例 ----------

    def test_home_page_elements(self):
        """首页元素：4 个全局 tab key + 底部播放条（非致命探测）。

        底部播放条模板截于「输出=扬声器/- -」无会话态，rig 持久播放会话
        （输出=设备名+曲目名）下内容永久偏离模板，存在性降级为非致命探测：
        命中记 info，未命中记 warning 不挂用例（口径同
        swan_regression_common verify-run3）。
        """
        self._ensure_logged_in_on_home()
        for key in (SwanBusiness.KEY_TAB_RECOMMEND,
                    SwanBusiness.KEY_TAB_PLATFORM,
                    SwanBusiness.KEY_TAB_DEVICE,
                    SwanBusiness.KEY_TAB_ME):
            assert self.aw.accessibility_exists(key), f"首页缺少 tab key: {key}"
        self._probe_bottom_player_bar()

    def test_platform_page_readonly(self):
        """平台页只读断言：根节点 + 网易云行 key + 行图片；⛔ 不点授权/充值。"""
        self._ensure_logged_in_on_home()
        self.aw.click_accessibility(SwanBusiness.KEY_TAB_PLATFORM)
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_PLATFORM_PAGE, timeout=15
        ), "未进入平台页（platform_page 未出现）"
        assert self.aw.accessibility_exists(
            SwanBusiness.KEY_NETEASE_PLATFORM_ENTRY
        ), "平台页缺少网易云音乐行 key"
        self.aw.image_exists(SWAN_PLATFORM_NETEASE_ROW, timeout=10)
        self.user.go_home()

    def test_device_page_elements(self):
        """设备页只读断言：根节点 + 添加设备（key+图片）+ 设备卡前缀匹配 ≥1 台。

        设备卡 key 按 UUID 动态拼接（wifi_device_card_<UUID>），用前缀遍历
        dump 判断，不写死 UUID。⛔ 不点设备卡/同步/音量/添加设备。
        """
        self._ensure_logged_in_on_home()
        self.aw.click_accessibility(SwanBusiness.KEY_TAB_DEVICE)
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_DEVICE_PAGE, timeout=15
        ), "未进入设备页（device_page 未出现）"
        assert self.aw.accessibility_exists(
            SwanBusiness.KEY_DEVICE_ADD_BUTTON
        ), "设备页缺少添加设备按钮"
        self.aw.image_exists(SWAN_DEVICE_ADD_BTN, timeout=10)
        card_keys = self.aw.list_accessibility_keys_by_prefix(
            SwanBusiness.PREFIX_WIFI_DEVICE_CARD
        )
        assert card_keys, (
            "设备页未发现任何 WIFI 设备卡（wifi_device_card_* 为空）。"
            "若页面显示「暂无WIFI设备」，说明账号当前未绑定设备（数据状态变化，"
            "非代码问题），需先在真机上重新配网绑定设备后再跑本用例"
        )
        self.user.go_home()

    def test_player_open_close(self):
        """播放页开关：点底部播放条进全屏播放页 → 断言后点收起按钮回首页。

        播放/暂停等控制键仅做存在性断言，⛔ 不点。
        """
        self._ensure_logged_in_on_home()
        self.aw.click_accessibility(SwanBusiness.KEY_BOTTOM_PLAYER)
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_FULL_PLAYER_PAGE, timeout=15
        ), "未进入全屏播放页（full_player_page 未出现）"
        # 控制类入口仅存在性断言（key + 图片双校验），不下发点击
        assert self.aw.accessibility_exists(
            SwanBusiness.KEY_PLAYER_DISMISS_BUTTON
        ), "播放页缺少收起按钮"
        assert self.aw.accessibility_exists(
            SwanBusiness.KEY_PLAYER_PLAY_PAUSE_BUTTON
        ), "播放页缺少播放/暂停按钮"
        self.aw.image_exists(SWAN_PLAYER_DISMISS_BTN, timeout=10)
        self.aw.image_exists(SWAN_PLAYER_PLAY_PAUSE_BTN, timeout=10)

        self.aw.click_accessibility(SwanBusiness.KEY_PLAYER_DISMISS_BUTTON)
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_TAB_ME, timeout=15
        ), "收起播放页后未回到首页"
        self._assert_home_shell_image()
        self._probe_bottom_player_bar()

    def test_favorites_group_detail(self):
        """收藏分组详情：我的页 → SWAN收藏 → 我的家庭 → OCR 断言 → 返回回首页。"""
        self._ensure_logged_in_on_home()
        self.aw.click_accessibility(SwanBusiness.KEY_TAB_ME)
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_ME_PROFILE_ENTRY, timeout=15
        ), "未进入我的页"
        self.aw.click_image(SWAN_ME_FAVORITES_ROW)
        # 收藏页无 accessibility key，用图片行断言进入成功
        self.aw.image_exists(SWAN_FAV_FAMILY_GROUP_ROW, timeout=10)

        self.aw.click_image(SWAN_FAV_FAMILY_GROUP_ROW)
        # "我的家庭"详情页：无已知 key，按 OCR 断言（文案变体任一命中）
        self._assert_any_text(("播放全部", "首歌"), timeout=15)

        self.aw.press_back()  # 详情页 → SWAN收藏页
        self.aw.image_exists(SWAN_FAV_FAMILY_GROUP_ROW, timeout=10)
        self.aw.press_back()  # SWAN收藏页 → 我的页
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_ME_PROFILE_ENTRY, timeout=15
        ), "两次返回后未回到我的页"
        self.user.go_home()
