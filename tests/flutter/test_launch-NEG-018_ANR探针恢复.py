# CASE-ID: launch-NEG-018
"""Swan 回归·M01 启动与隐私：冷启动 ANR 探针与预案恢复链路（launch-NEG-018）。

用例 → AW 映射：
- ANR 探针（P-003 前置门）→ [OCR]「无响应」/「isn't responding」弹窗探测
- 预案恢复（等待×1 → force-stop 冷重启）→ 宽限窗口复探（代替硬等待）
  + cold_start_assert("home")（内部 stop_app+start_app 即杀进程冷重启）
- 重启后状态一致性 → cold_start_assert(landed="home")（已同意+登录态落首页）
step4 结果登记为执行纪律（未稳定复现不提单、登记 flaky 候选批），
不在脚本内表达，由平台执行结果页承载。
清理：无（状态一致性由冷启动断言收口）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestLaunchNeg018AnrProbeRecover(SwanRP01Mixin, BaseTest):
    """冷启动 ANR 探针与预案恢复（launch-NEG-018）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_cold_start_anr_probe_and_recover(self):
        """冷启动 ANR 探针；命中则执行等待+冷重启预案，终态断言落首页。"""
        anr = (self.userA.find_text_by_ocr("无响应", timeout=3) is not None
               or self.userA.find_text_by_ocr("isn't responding",
                                              timeout=3) is not None)
        if anr:
            # 预案等待×1：宽限窗口内复探（带 timeout 的探测，非硬等待）；
            # 无论是否自愈，下一步 force-stop 冷重启均为预案的恢复动作，
            # 复现登记为执行纪律不在脚本内表达
            self.userA.find_text_by_ocr("无响应", timeout=10)
        # force-stop 冷重启 + 重启后状态一致性（已同意+登录态 → 落首页）
        self.userA.cold_start_assert(landed="home")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
