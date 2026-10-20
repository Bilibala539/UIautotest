# CASE-ID: push-POS-004
"""Swan 回归·推送：非强更弹窗展示与「稍后更新」安全关闭（push-POS-004，部分转换）。

步骤 -> AW 映射（服务端预置非强更新版本（updateType!=0 且高于本地），
用例后人工回滚；禁区 1：绝不点「立即更新」——真下载 APK+拉安装器）：
- 步骤0 进关于页触发检查 -> go_bottom_tab('我的') + click_any_text
  ('关于与升级'/'关于' 候选）+ click_text('软件升级')；
- 步骤1 非强更弹窗弹出 -> find_text_by_ocr('立即更新') 探测，服务端
  预置缺失时运行时 skip；
- 步骤2/3 校验双按钮完整（标题/说明为图像级形态，模板未入库登记
  template_needs；「稍后更新」在位=非强更双按钮形态，强更单按钮
  形态不触达——禁区 3 围栏由「稍后更新」存在性断言承担）；
- 步骤4 点击「稍后更新」关闭（唯一安全关闭路径，dismissedLater 节流）
  -> click_text('稍后更新') + text_not_exists('立即更新') + 关于页存活，
  全程零下载零跳转（无「立即更新」点击即围栏成立的黑盒证据）。

清理：服务端版本配置回滚为人工流程（见 package_report.notes）；
teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestUpgradeDialogNonForce(BaseTest):
    """push-POS-004：非强更弹窗双按钮展示，稍后更新安全关闭。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_upgrade_dialog_non_force_close(self):
        """弹窗双按钮在位，稍后更新关闭后无残留。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        # 步骤0：关于页手动触发检查
        self.userA.click_any_text("关于与升级", "关于")
        self.userA.assert_any_of_texts("软件升级", "版本", timeout=8)
        self.userA.click_any_text("软件升级", "检查更新")
        # 步骤1：非强更弹窗出现（环境预置缺失则 skip）
        if self.userA.find_text_by_ocr("立即更新", timeout=8) is None:
            pytest.skip("升级弹窗未出现（服务端非强更新版本未预置），转环境预置")
        # 步骤2/3：双按钮完整（稍后更新在位，强更单按钮形态不触达）
        self.userA.assert_any_of_texts("稍后更新", timeout=5)
        # 步骤4：稍后更新安全关闭（唯一合法路径）
        self.userA.click_text("稍后更新", timeout=5)
        self.userA.text_not_exists("立即更新", timeout=3)
        self.userA.assert_any_of_texts("软件升级", "关于", "版本", timeout=8)

    def teardown(self) -> None:
        """冷启动模型：App 冷启动由框架夹具承担（服务端配置回滚为人工流程）。"""
        pass
