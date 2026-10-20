# CASE-ID: settings-POS-003
"""Swan 回归·M17 设置/切服/平台通道:弹层选项集与可选集一致(settings-POS-003)。

用例 -> AW 映射:
- 步骤3(UI 面)切服弹层选项与可选集一致性 -> open_about_detail +
  probe_tap_server_logo(Logo 模板未截获/Release 无手势 -> 运行期条件 skip)
  -> assert_server_switch_sheet:UI 展示集合(测试服/正式服/本地环境 [OCR])
  与单测可选集 [staging,production,local] 一致,development 任何包型不可达
- 步骤1/2/4 单测层(selectableValues==三值 / development ArgumentError 守卫 /
  持久化键名 hivi.server_environment 契约)-> 单测/白盒面,框架无此通道,
  分轨登记 notes
禁区围栏(M17 禁区 1):只断言弹层选项展示,绝不点击任何环境选项。
cleanup:close_server_switch_sheet 承载(未切换,无状态残留)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestServerSheetSetConsistent(SwanRP10Mixin, BaseTest):
    """切服可选集三值现状:UI 展示集合一致性(settings-POS-003)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_server_sheet_ui_set_consistent(self):
        """UI 展示选项与可选集一致(三值,development 缺席)。"""
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
