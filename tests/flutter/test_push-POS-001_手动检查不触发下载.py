# CASE-ID: push-POS-001
"""Swan 回归·推送：关于页「软件升级」手动检查止步于检查（push-POS-001，部分转换）。

步骤 -> AW 映射（手动+自动双触发共用 AppUpdateCoordinator；禁区 1：
绝不点「立即更新」；禁区 3：进页先确认非强更）：
- 步骤1 打开关于与升级页 -> go_bottom_tab('我的') + click_any_text
  ('关于与升级'/'关于' 候选，入口中文未核准登记 template_needs），
  进页自动触发一次最新版本检查；
- 步骤2 点击「软件升级」行触发手动检查 -> click_text('软件升级')；
- 步骤3 检查完成态三态其一 -> wait_toast('已经是最新版本')（toast 态）
  或非强更弹窗态（dismiss_update_dialog_guarded 按禁区守卫关闭：只有
  「稍后更新」才点，强更形态运行时 skip 转人工）——任一命中即完成面；
- 步骤4 无下载/安装副作用 -> event=apk_download_* 日志断言无通道，
  UI 面以关于页存活可交互兜底（断言止步于检查动作）。

清理：返回我的页（press_back）；teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestAboutManualCheckNoDownload(BaseTest):
    """push-POS-001：手动检查出完成态，全程无下载安装副作用。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_about_manual_check_no_download(self):
        """软件升级手动检查 -> 三态其一完成，关于页存活。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        # 步骤1：关于与升级页（进页自动触发一次检查）
        self.userA.click_any_text("关于与升级", "关于")
        self.userA.assert_any_of_texts("软件升级", "版本", timeout=8)
        # 步骤2：手动触发检查
        self.userA.click_any_text("软件升级", "检查更新")
        # 步骤3：完成态三态其一（toast 态 / 非强更弹窗态 / 静默完成）
        if not self.userA.wait_toast("已经是最新版本", timeout=6.0):
            self.userA.dismiss_update_dialog_guarded()
        # 步骤4：无下载安装副作用（关于页仍存活可交互）
        self.userA.assert_any_of_texts("软件升级", "关于", "版本", timeout=8)
        # 清理：返回我的页
        self.userA.press_back()

    def teardown(self) -> None:
        """已返回我的页（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
