# CASE-ID: help-POS-012
# LINKED-CASE: M15-POS-012
"""Swan 回归·M15 帮助与反馈:关于与升级页可达且 4 行与版本标签(help-POS-012)。

用例 -> AW 映射:
- 进入我的页点击「关于与升级」入口 -> go_bottom_tab("我的") +
  open_about_page(open_me_row 遮挡上滑口径)[OCR]
- 固定 4 行顺序(关于/使用政策/隐私政策/软件升级)-> find_text_by_ocr
  取 y 序严格递增断言(知识库 swan_关于与升级页实测行名)[OCR]
- 版本标签两行式 -> text_exists("build")(第二行 "(build n)" OCR;
  字形变体登记 template_needs)
- 可升级角标分支 -> 服务端与本地版本比对属动态数据,登记 notes

清理:go_home(只读浏览)。
"""
from __future__ import annotations

from conftest import BaseTest


class TestHelpPos012(BaseTest):
    """关于与升级页可达且 4 行与两行式版本标签渲染。"""

    def setup(self) -> None:
        """测试前初始化:实例化用户对象(用户信息挂在 userA 上)。"""
        self.userA = self.users("swanuserA")

    def test_about_upgrade_page_rows_and_version(self):
        """关于与升级页打开,4 行按序渲染,版本标签含 (build n) 行。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        self.userA.open_about_page()
        rows = ("关于我们", "使用政策", "隐私政策协议", "软件升级")
        ys = []
        for row in rows:
            pos = self.userA.find_text_by_ocr(row, timeout=8)
            assert pos is not None, f"关于与升级页缺少行锚「{row}」[OCR]"
            ys.append(pos[1])
        assert ys == sorted(ys), (
            f"关于与升级页 4 行顺序错误,y 序列 {ys}")
        self.userA.text_exists("build", timeout=8)
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理(冷启动模型:App 冷启动由框架夹具承担)。"""
        pass
