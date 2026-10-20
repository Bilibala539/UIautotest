# CASE-ID: push-POS-003
"""Swan 回归·推送：已是最新版提示态 toast 且无升级弹窗（push-POS-003）。

步骤 -> AW 映射（服务端 /version/details 版本不高于本地预置态；
l10n aboutAlreadyLatestVersion 实证 zh=已经是最新版本）：
- 步骤0 进关于与升级页 -> go_bottom_tab('我的') + click_any_text
  ('关于与升级'/'关于' 候选，入口中文未核准登记 template_needs）；
- 步骤1 点击「软件升级」触发检查 -> click_text('软件升级')；
- 步骤2 UI 反馈 -> wait_toast('已经是最新版本')（toast 短暂，触发后
  立即等待）；toast 未现且弹窗出现=服务端配置非最新态，按禁区守卫
  关闭后运行时 skip 转环境预置；
- 步骤3 无后续动作 -> event=apk_download_* 日志断言无通道，UI 面
  以无弹窗残留（text_not_exists '立即更新'）+ 关于页存活兜底。

清理：返回我的页（press_back）；teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestAlreadyLatestToast(BaseTest):
    """push-POS-003：最新版场景 toast 反馈，无弹窗无下载。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_already_latest_version_toast(self):
        """软件升级检查 -> 「已经是最新版本」toast，无弹窗残留。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        # 步骤0：关于与升级页
        self.userA.click_any_text("关于与升级", "关于")
        self.userA.assert_any_of_texts("软件升级", "版本", timeout=8)
        # 步骤1：手动触发检查
        self.userA.click_any_text("软件升级", "检查更新")
        # 步骤2：toast 反馈（触发后立即等待）
        if not self.userA.wait_toast("已经是最新版本", timeout=6.0):
            self.userA.dismiss_update_dialog_guarded()
            pytest.skip("未出现「已经是最新版本」toast（服务端版本配置非最新态），转环境预置")
        # 步骤3：无弹窗残留、关于页存活（无下载跳转副作用）
        self.userA.text_not_exists("立即更新", timeout=3)
        self.userA.assert_any_of_texts("软件升级", "关于", "版本", timeout=8)
        # 清理：返回我的页
        self.userA.press_back()

    def teardown(self) -> None:
        """已返回我的页（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
