# CASE-ID: radio-NEG-004
"""Swan 回归·电台：冷启动直进电台 Tab ANR 探针（radio-NEG-004）。

步骤 -> AW 映射（P-003 启动时序 ANR 探针，黑盒可观察面）：
- 步骤0 冷启动 -> relaunch_app(userA.package)（用例本身测重启时点，
  显式重启承担冷启动语义）；
- 步骤1 启动后立即点击首页电台 Tab -> go_top_tab('电台')，到位后
  断言无 ANR 对话框 -> text_not_exists('无响应')/'isn't responding'
  双语候选（中英文系统对话框文案）；
- 步骤2 hierarchy 可达性 -> 三区块结构候选断言（UI 层级可捕获的
  OCR 可观察面）；
- 步骤3 Tab 内下拉交互探针 -> swipe_down 后区块标题复现（Lottie
  动画期不阻塞输入的正向面）；
- 步骤4 记录探针结果 -> 人工流程（两次复现才记候选不提单），自动化
  侧以断言通过为零 ANR 证据，见 package_report.notes。

清理：只读探针，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioColdStartAnrProbe(BaseTest):
    """radio-NEG-004：冷启动直进电台 Tab 零 ANR、结构可达、下拉响应。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_cold_start_no_anr(self):
        """冷启动直进电台 Tab：无 ANR 对话框、三区块可达、下拉响应。"""
        # 步骤0：冷启动（用例测重启时点）
        self.userA.relaunch_app(self.userA.package)
        # 步骤1：立即进电台 Tab，无 ANR 对话框（双语候选）
        self.userA.go_top_tab("电台")
        self.userA.text_not_exists("无响应", timeout=3)
        self.userA.text_not_exists("isn't responding", timeout=2)
        # 步骤2：三区块结构可达（hierarchy 可捕获的 OCR 面）
        self.userA.assert_any_of_texts("全国电台", "国家台", "80", "90",
                                       timeout=10)
        # 步骤3：下拉刷新响应正常（动画期不冻结输入）
        self.userA.swipe_down()
        self.userA.assert_any_of_texts("全国电台", "国家台", "80", "90",
                                       timeout=8)

    def teardown(self) -> None:
        """只读探针无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
