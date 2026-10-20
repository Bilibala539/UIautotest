# CASE-ID: settings-NEG-005
"""Swan 回归·M17 设置/切服/平台通道:切服弹层展示即止零登出(settings-NEG-005)。

用例 -> AW 映射:
- 步骤1 非 Release 包进关于我们三级页点击 Logo -> open_about_detail +
  probe_tap_server_logo(Logo 模板未截获/Release 无手势 -> 运行期条件 skip)
  -> 弹层出三个环境选项 assert_server_switch_sheet(测试服/正式服/本地环境)
  ——禁区 1 即止
- 步骤2 关闭弹层返回 -> close_server_switch_sheet:双 press_back 退回
  关于与升级页 + 「软件升级」行 [OCR] 复核(环境未变、token 未动、零登出
  副作用的 UI 证据:仍停在关于页而非登录页)
- 步骤3 Release 包同位置无手势零响应 -> 需 Release 构建通道,执行器包型
  不可控,分轨登记 notes(非 Release 误跑会开弹层,违禁区 1)
- 步骤4 单测层断言切服清 token 闭合链 -> 单测/白盒面,框架无此通道,分轨
禁区围栏(M17 禁区 1):断言到弹层展示即止,绝不点击任何环境选项。
cleanup:close_server_switch_sheet 承载(未切换,无状态残留)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p10 import SwanRP10Mixin


class TestServerSheetNoLogout(SwanRP10Mixin, BaseTest):
    """切服清 token 链守卫:UI 面弹层即止+关闭零登出(settings-NEG-005)。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_server_sheet_close_no_logout(self):
        """弹层三选项展示即止,关闭后停留关于页零登出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_about_detail()
        if not self.userA.probe_tap_server_logo():
            pytest.skip("切服 Logo 模板未截获(198×80 资产待截取注册)或弹层未"
                        "弹出(Release 包无手势/弹层锚待校准)——B 轨模板门禁,"
                        "template_needs 已登记")
        self.userA.assert_server_switch_sheet()
        self.userA.close_server_switch_sheet()
        # 步骤2 围栏合规核对:环境未变、零登出——仍在关于与升级页内层
        assert self.userA.find_text_by_ocr("软件升级", timeout=5) is not None, (
            "关闭弹层后关于与升级页不完整(「软件升级」行未命中)——疑发生"
            "环境切换/登出副作用")

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
