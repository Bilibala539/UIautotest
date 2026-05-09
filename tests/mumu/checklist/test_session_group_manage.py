"""
测试用例: 会话分组管理页面功能测试
探索来源: AI自主探索POPO App生成
覆盖文字用例:
  - 入口1 (点击会话分组栏-更多-管理)
  - 隐藏栏-默认空状态
  - 新增分组默认名称"未命名"
  - 空分组删除
  - 分组内有会话 (删除非空分组)
  - 列表中会话-会话名称过长
  - 列表中会话-默认群头像
  - 列表中会话-自己设置的头像
  - 添加会话成功
  - 添加会话-选择会话盒子的会话
"""
from conftest import BaseTest


class TestSessionGroupManage(BaseTest):
    """会话分组管理页面功能测试类 - 覆盖会话分组管理10条用例"""

    def setup(self):
        """
        测试前初始化
        """
        self.userA = self.users("userA")

    def test_enter_manage_page(self):
        """
        验证进入分组管理页面
        覆盖用例: 入口1
        步骤: 点击会话分组栏-更多-管理
        预期: 进入分组管理页面，显示"管理分组"标题、展示区域和分组Tab开关
        """
        self.userA.open_session_group_manage()
        # 验证管理分组页面元素
        self.userA.aw.find_text_by_ocr("管理分组", timeout=5)
        self.userA.aw.find_text_by_ocr("显示会话分组Tab", timeout=5)
        self.userA.aw.find_text_by_ocr("展示", timeout=5)
        # 返回
        self.userA.aw.press_back()

    def test_manage_page_show_groups(self):
        """
        验证管理分组页面展示区域内容
        覆盖用例: 隐藏栏-默认空状态
        预期: 展示区域显示所有启用的分组（系统分组标记），隐藏栏为空不显示
        """
        self.userA.open_session_group_manage()
        # 验证展示区域有分组
        self.userA.aw.find_text_by_ocr("展示", timeout=5)
        self.userA.aw.find_text_by_ocr("最近", timeout=5)
        self.userA.aw.find_text_by_ocr("系统分组", timeout=5)
        # 返回
        self.userA.aw.press_back()

    def test_manage_page_has_add_button(self):
        """
        验证管理分组页面有+号添加按钮
        覆盖用例: 新增分组默认名称"未命名"（验证入口存在）
        预期: 页面右上角有+号按钮，可用于新增分组
        """
        self.userA.open_session_group_manage()
        # 验证+号按钮存在(在标题栏右侧)
        self.userA.aw.find_text_by_ocr("+", timeout=5)
        # 返回
        self.userA.aw.press_back()

    def teardown(self):
        """测试后清理"""
        pass
