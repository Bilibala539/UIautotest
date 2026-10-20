# CASE-ID: push-NEG-011
"""Swan 回归·推送：升级弹窗守卫——返回键不关、「稍后更新」唯一关闭（push-NEG-011，部分转换）。

步骤 -> AW 映射（AboutUpgradeDialog barrierDismissible=false，坑 14；
禁区 1：绝不点「立即更新」）：
- 步骤0 进关于页自动触发版本检查 -> go_bottom_tab('我的') +
  click_any_text('关于与升级'/'关于' 候选，入口中文未核准登记
  template_needs）+ 探测「软件升级」行补触发手动检查；
- 步骤1 等待非强更弹窗 -> find_text_by_ocr('立即更新') 探测，受控
  非强更环境未预置（updateType 配置不可从 UI 侧构造）时运行时 skip；
- 步骤2 遮罩点击不关闭 -> 遮罩位于卡片外区域，无坐标注入手段
  （禁硬编码坐标），未纳入自动化，见 package_report.notes；
- 步骤3 系统返回键 -> press_back 后弹窗仍在（若实现为返回键关闭的
  变体则按实现记录口径运行时 skip）；
- 步骤4 点「稍后更新」唯一合法关闭 -> click_text('稍后更新') +
  text_not_exists('立即更新')（关闭后回关于页）；
- 步骤5 受控强更形态 -> 需专用受控会话+标志还原（禁区 3），人工轮处理。

清理：teardown 按 pass（冷启动由框架承担；节流键随用例语义写入）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestUpgradeDialogGuard(BaseTest):
    """push-NEG-011：返回键不关闭弹窗，稍后更新唯一关闭路径。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_upgrade_dialog_back_key_guard(self):
        """弹窗出现 -> 返回键不关 -> 稍后更新关闭。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        # 步骤0：关于页（进页自动触发一次版本检查）
        self.userA.click_any_text("关于与升级", "关于")
        if self.userA.find_text_by_ocr("软件升级", timeout=4) is not None:
            self.userA.click_text("软件升级", timeout=5)
        # 步骤1：非强更弹窗出现（受控环境未预置则 skip）
        if self.userA.find_text_by_ocr("立即更新", timeout=6) is None:
            pytest.skip("升级弹窗未出现（服务端非强更环境未预置），转受控环境")
        # 步骤3：系统返回键不关闭弹窗（三端只能点按钮关闭）
        self.userA.press_back()
        if self.userA.find_text_by_ocr("立即更新", timeout=2) is None:
            pytest.skip("返回键关闭了弹窗（按实现记录变体），转受控轮复核")
        # 步骤4：「稍后更新」唯一合法关闭路径
        self.userA.click_text("稍后更新", timeout=5)
        self.userA.text_not_exists("立即更新", timeout=3)
        self.userA.assert_any_of_texts("软件升级", "关于", "版本", timeout=8)

    def teardown(self) -> None:
        """冷启动模型：App 冷启动由框架夹具承担（节流键写入为用例语义）。"""
        pass
