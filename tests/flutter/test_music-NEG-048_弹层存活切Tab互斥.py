# CASE-ID: music-NEG-048
"""Swan 回归·M07 平台授权:授权弹层存活时切平台入口→互斥不叠加(music-NEG-048)。

步骤→AW 映射(坑 7 挂起互斥家族,授权单飞锁语义):
  1. 发起 QQ 授权至进度弹层存活 → tap_platform_row_plus('qq')
     + confirm_auth_dialog(),「取消」钮 [OCR] 探活
  2. 弹层存活时底栏 Tab 往返(平台→首页→平台) → go_bottom_tab 双跳;弹层
     随栈恢复或明确关闭为 YAML 双口径,均合法,不设单态断言
  3. 点第二平台行 [+] 观察互斥 → tap_platform_row_plus(第二平台),互斥族
     双口径:auth_in_progress 定向提示(wait_toast)或 QQ 挂起被取消后第二
     平台链路放行(确认弹层/H5 登录页);二者必居其一

cleanup: dismiss_auth_popup 取消残留挂起,回平台页;框架每用例冷启动。
B 标定说明:第二平台按行授权态自适配(网易云未授权优先,否则 Qobuz;
网易云已授权为环境常态);互斥提示文案与进度弹层遮挡程度未标定
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_NETEASE_PLUS_BTN


class TestMusicNeg048PopupAliveTabMutex(BaseTest):
    """弹层存活 Tab 往返 + 跨平台发起:单授权锁互斥,不叠加。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_popup_alive_tab_switch_mutex(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "unauthorized":
            pytest.skip("QQ 行非未授权态,授权挂起链路无法从 [+] 发起(账号态自适配)")
        if self.userA.platform_row_state("netease") == "unauthorized":
            second = "netease"
        elif self.userA.platform_row_state("qobuz") == "unauthorized":
            second = "qobuz"
        else:
            pytest.skip(
                "无可用第二未授权平台行(网易云/Qobuz 均已授权),跨平台互斥无法发起")
        # 步骤 1:QQ 授权挂起,进度弹层存活
        self.userA.tap_platform_row_plus("qq")
        self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("取消", timeout=10) is not None, (
            "确认后授权进度弹层未出现(挂起未建立)")
        # 步骤 2:弹层存活时底栏 Tab 出走再回
        self.userA.go_bottom_tab("首页")
        self.userA.go_bottom_tab("平台")
        # 步骤 3:跨平台发起,互斥族双口径二者必居其一
        if second == "netease":
            self.userA.tap_platform_row_plus(
                "netease", template=SWAN_NETEASE_PLUS_BTN)
        else:
            self.userA.tap_platform_row_plus("qobuz")
        mutex_hint = self.userA.wait_toast("授权", timeout=4)
        if not mutex_hint:
            if self.userA.find_text_by_ocr("确认", timeout=6) is not None:
                self.userA.confirm_auth_dialog()
            assert self.userA.find_text_by_ocr("登录", timeout=20) is not None, (
                "跨平台发起既无互斥提示也未放行第二平台链路(单授权锁语义未观测)")
            self.userA.press_back()
        # 终态收束:取消残留挂起,平台页无错误提示
        self.userA.dismiss_auth_popup()
        self.userA.assert_no_auth_error()
