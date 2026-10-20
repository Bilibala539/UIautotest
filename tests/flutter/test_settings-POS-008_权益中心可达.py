# CASE-ID: settings-POS-008
"""Swan 回归·M17 设置/切服/平台通道:权益中心 App Bridge 页可达(settings-POS-008)。

用例 -> AW 映射:
- 步骤1 从我的域打开权益中心 -> open_rights_center:我的 tab [图] ->
  「我的权益」功能行 [OCR](遮挡时上滑重试) -> 容器页锚「权益中心」[OCR]
  (H5 装载完成的 UI 粗判据)
- 步骤2/3 校验加载域(host 白名单/HTTPS/port)与双桥隔离 -> 日志断言面,
  不在 UI 自动化轨,已登记 notes
- 步骤4 等待页面装载(15s watchdog) -> 容器页锚 [OCR] 带 20s 超时承载
- cleanup -> close_rights_center:press_back 回我的页(「我的权益」行 [OCR] 断言)

B 轨登记:容器页标题文案「权益中心」与「我的权益」行在页内出现两次
(标题行+可点击行)的点击命中面,首跑校准;见 package_report.json
template_needs。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestRightsCenterReachable(SwanRP10Mixin, BaseTest):
    """权益中心 App Bridge 页可达:白名单 H5 无崩溃(settings-POS-008)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_rights_center_reachable(self):
        """权益中心经新协议容器可达且装载完成,退出回我的页。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_rights_center_from_tab()
        # H5 装载粗判据已由 open_rights_center 的容器页锚 [OCR] 断言承载;
        # 白名单 host/双桥隔离为日志面,不在 UI 轨(见 docstring 与 notes)
        self.userA.close_rights_center()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
