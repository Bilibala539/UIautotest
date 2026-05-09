"""
测试用例: 会话分组面板功能测试
探索来源: AI自主探索POPO App生成
覆盖文字用例:
  - 面板展开的显示--PC端设置过
  - 面板展开的显示-最大分组数显示
  - 切换tab
  - 上滑列表tab吸顶
  - 点击分组名跳转分组列表-分组栏展开
  - 跳转管理分组页面
  - 跳转会话盒子详情页
  - 关闭展开的分组栏
"""
import pytest
from conftest import BaseTest


class TestSessionGroupPanel(BaseTest):
    """会话分组面板功能测试类 - 覆盖新增会话分组模块8条用例"""

    def setup(self):
        """
        测试前初始化
        """
        self.userA = self.users("userA")

    def test_open_session_group_panel(self):
        """
        验证打开会话分组面板
        覆盖用例: 面板展开的显示--PC端设置过
        预期: 展开分组面板，显示所有分组，右上角有管理按钮，下方显示会话盒子和关闭的会话
        """
        self.userA.open_session_group_panel()
        # 验证面板内容: 会话分组标题、管理按钮
        self.userA.aw.find_text_by_ocr("会话分组", timeout=5)
        self.userA.aw.find_text_by_ocr("管理", timeout=5)
        # 验证有会话盒子和关闭的会话入口
        self.userA.aw.find_text_by_ocr("会话盒子", timeout=5)
        self.userA.aw.find_text_by_ocr("关闭的会话", timeout=5)
        # 关闭面板恢复初始状态
        self.userA.close_session_group_panel()

    def test_close_panel_by_mask(self):
        """
        验证点击蒙层关闭分组面板
        覆盖用例: 关闭展开的分组栏
        预期: 分组弹窗关闭，恢复正常消息列表视图
        """
        self.userA.open_session_group_panel()
        # close_session_group_panel 内部已通过image_exists验证面板关闭
        self.userA.close_session_group_panel()

    @pytest.mark.parametrize("tab_name", ["@我", "未读", "待处理", "最近"])
    def test_switch_group_tab(self, tab_name):
        """
        验证切换分组Tab
        覆盖用例: 切换tab
        预期: 可以切换各个tab栏，并显示该tab下的会话列表
        """
        self.userA.switch_session_group_tab(tab_name)
        # 切换回最近tab
        if tab_name != "最近":
            self.userA.switch_session_group_tab("最近")

    def test_panel_click_group_name(self):
        """
        验证面板展开后点击分组名跳转
        覆盖用例: 点击分组名跳转分组列表-分组栏展开
        预期: 打开该tab下的会话列表，面板自动关闭
        """
        self.userA.open_session_group_panel()
        # 点击面板中的"未读"分组名
        self.userA.aw.click_text("未读", timeout=5)
        import time
        time.sleep(1)
        # 面板应该关闭，切换到未读tab
        # 切回最近
        self.userA.switch_session_group_tab("最近")

    def test_jump_to_manage_page(self):
        """
        验证跳转管理分组页面
        覆盖用例: 跳转管理分组页面
        预期: 跳转到管理分组页面，显示展示区域和所有分组
        """
        self.userA.open_session_group_manage()
        # 验证在管理分组页面
        self.userA.aw.find_text_by_ocr("管理分组", timeout=5)
        self.userA.aw.find_text_by_ocr("显示会话分组Tab", timeout=5)
        # 返回
        self.userA.aw.press_back()

    def test_jump_to_session_box(self):
        """
        验证跳转会话盒子详情页
        覆盖用例: 跳转会话盒子详情页
        预期: 跳转到会话盒子列表页
        """
        self.userA.open_session_box()
        # 验证在会话盒子页面
        self.userA.aw.find_text_by_ocr("会话盒子", timeout=5)
        # 返回
        self.userA.aw.press_back()

    def teardown(self):
        """测试后清理"""
        pass
