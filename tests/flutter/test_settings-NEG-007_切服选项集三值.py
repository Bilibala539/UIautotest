# CASE-ID: settings-NEG-007
"""Swan 回归·M17 设置/切服/平台通道:切服选项集三值 development 不可达(settings-NEG-007)。

用例 -> AW 映射:
- 步骤1 非 Release 包打开切服弹层核对选项集 -> open_about_detail +
  probe_tap_server_logo(Logo 模板未截获/Release 无手势 -> 运行期条件 skip)
  -> assert_server_switch_sheet(测试服/正式服/本地环境三选项 [OCR]) +
  text_not_exists("development")(development 不在可选集的 UI 面证据)
- 步骤2/3 单测层(switchTo('development') ArgumentError 守卫 + HIVI_NETWORK_ENV
  四值映射识别序)-> 单测/白盒面,框架无此通道,分轨登记 notes
禁区围栏(M17 禁区 1/2):断言到弹层展示即止,绝不点击任何环境选项;
switchTo 守卫只在单测层闭合。
cleanup:close_server_switch_sheet 承载(未切换,无状态残留)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestServerSheetThreeOptions(SwanRP10Mixin, BaseTest):
    """development 环境不可达守卫:UI 选项集恰三值(settings-NEG-007)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_server_sheet_option_set_exact(self):
        """弹层选项集恰为三值,development 不在可选集。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_about_detail()
        if not self.userA.probe_tap_server_logo():
            pytest.skip("切服 Logo 模板未截获(198×80 资产待截取注册)或弹层未"
                        "弹出(Release 包无手势/弹层锚待校准)——B 轨模板门禁,"
                        "template_needs 已登记")
        self.userA.assert_server_switch_sheet()
        self.userA.text_not_exists("development")
        self.userA.close_server_switch_sheet()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
