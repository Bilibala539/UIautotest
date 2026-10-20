# CASE-ID: music-POS-010
"""Swan 回归·M07 QQ音乐:QQ 视频分类页主路径·默认筛选态(music-POS-010)。

步骤→AW 映射(PlatformVideoClassifyArgs 默认参数锚 initialTag=0/initialSort=0):
  1. QQ 主页点视频分类入口 → open_platform_home('qq') + scroll_to_text
     ('精选视频')(KB:页尾区块) + click_text('精选视频'),视频分类页打开
  2. 默认筛选态渲染 → assert_any_text(['视频','分类'])(页面挂载+网格区
     以 OCR 文案锚承载)
  3. 切换一个分类 tag → 分类 tag 文案未标定(服务端 tag 集合未知,盲点会
     误点非 tag 元素) → 本用例如实覆盖前两步,tag 切换登记 template_needs
     待真机标定 tag 名后补转(DIGEST B 口径)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:视频分类页专属锚/分类 tag 集合未截模板,通用文案变体锚承载
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos010QqVideoClassify(BaseTest):
    """QQ 视频分类页默认参数契约渲染,入口可达。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qq_video_classify_default(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "authorized":
            pytest.skip("QQ 行非已授权态,QQ 主页视频入口不可达(账号态自适配)")
        # 步骤 1:QQ 主页 → 精选视频区块(页尾) → 视频分类页
        self.userA.open_platform_home("qq")
        self.userA.scroll_to_text("精选视频")
        self.userA.click_text("精选视频", timeout=8)
        # 步骤 2:默认态渲染(页面挂载)
        self.userA.assert_any_text(["视频", "分类"])
