# CASE-ID: settings-POS-002
"""Swan 回归·M17 设置/切服/平台通道:非 Release 切服弹层展示与取消(settings-POS-002)。

用例 -> AW 映射:
- 步骤1 打开关于我们三级页点击 Logo -> open_about_detail(我的 tab [图] ->
  上滑两屏 -> 「关于与升级」[OCR] -> 「关于我们」[OCR]) + probe_tap_server_logo
  (Logo 198×80 图像资产无 OCR 文案,模板未截获时按「模板未截获」条件 skip;
  模板就绪后点击并探测弹层标题「选择服务器」[OCR],Release 无手势同样条件
  skip——不误报缺陷)
- 步骤2 弹层选项集展示 -> assert_server_switch_sheet:测试服/正式服 [OCR] +
  第三选项(本地环境/本地服)双候选探测
- 步骤3 点返回关闭弹层不选任何项 -> close_server_switch_sheet:双 press_back
  退回关于与升级页(标题 [OCR] 命中 = 无环境切换、无登出)
禁区围栏(M17 禁区 1):只验证弹层展示与取消路径,绝不点击任何服务器选项
——真实切服会立即本地登出清 token。
状态条件用例:Logo 模板未截获/Release 包无手势 -> 运行期条件 skip。
cleanup:close_server_switch_sheet 承载(关弹层+回关于与升级页)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestServerSheetShowCancel(SwanRP10Mixin, BaseTest):
    """非 Release 切服弹层展示(三选项)不选安全关闭(settings-POS-002)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_server_sheet_show_and_cancel(self):
        """切服弹层三选项展示正确,返回关闭零副作用。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_about_detail()
        if not self.userA.probe_tap_server_logo():
            pytest.skip("切服 Logo 模板未截获(198×80 资产待截取注册)或弹层未"
                        "弹出(Release 包无手势/弹层锚待校准)——B 轨模板门禁,"
                        "template_needs 已登记")
        self.userA.assert_server_switch_sheet()
        self.userA.close_server_switch_sheet()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
