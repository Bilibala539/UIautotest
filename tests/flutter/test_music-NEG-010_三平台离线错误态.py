# CASE-ID: music-NEG-010
"""Swan 回归·M07 平台内容页:三平台内容主页离线错误态(music-NEG-010)。

步骤→AW 映射(7.3 网易云域,断网维度,坑 17/坑 20 定位纪律):
  1. 开飞行模式 → toggle_airplane_mode(设置页 OCR 通道)
  2. 网易云内容主页 → open_platform_home("netease") → 离线错误/空态
     占位语义断言(错误态文案为未探索面,B 变体扫描:网络/加载失败/
     重试/连接/暂无;孤儿常量 neteaseContentLoading/Error 禁依赖)
  3. QQ/Qobuz 主页同断言,各行前置 platform_row_state 已授权闸门
     (自动化账号仅网易云恒已授权,未授权分支按账号态预置 skip)
  4. 恢复网络 → 重进网易云主页 → 内容自愈(每日/推荐/歌单锚回显)

cleanup: 网络恢复在正文内完成;teardown 按 _m07_airplane_on 旗标防御性
再切换一次(仅当正文失败于"已开飞行模式→未恢复"区间才动作)。
B 标定说明:三平台离线错误态真实文案与 Qobuz/QQ 主页入口锚待真机补截,
见 package_report.json template_needs。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicNeg010OfflineContentError(BaseTest):
    """三平台内容主页离线优雅降级、恢复自愈(语义定位)。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        # 用例私有清理:仅当正文失败于"已开飞行模式→未恢复"区间才切换
        if getattr(self, "_m07_airplane_on", False):
            self.userA.toggle_airplane_mode()
            self._m07_airplane_on = False

    def test_offline_content_error_states(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:断网
        self.userA.toggle_airplane_mode()
        self._m07_airplane_on = True
        # 步骤 2:网易云内容主页离线错误态
        self.userA.open_platform_home("netease")
        self.userA.assert_any_text(
            ("网络", "加载失败", "重试", "连接", "暂无", "错误"), timeout=12)
        self.userA.back_to_platform_page()
        # 步骤 3:QQ / Qobuz 分支(已授权闸门,未授权按账号态预置 skip)
        for platform in ("qq", "qobuz"):
            state = self.userA.platform_row_state(platform)
            if state != "authorized":
                pytest.skip(f"{platform} 主页需已授权预置,自动化账号态不可达")
            self.userA.open_platform_home(platform)
            self.userA.assert_any_text(
                ("网络", "加载失败", "重试", "连接", "暂无", "错误"), timeout=12)
            self.userA.back_to_platform_page()
        # 步骤 4:恢复网络 → 网易云内容自愈
        self.userA.toggle_airplane_mode()
        self._m07_airplane_on = False
        self.userA.open_platform_home("netease")
        self.userA.assert_any_text(("每日", "推荐", "歌单", "风格"), timeout=20)
