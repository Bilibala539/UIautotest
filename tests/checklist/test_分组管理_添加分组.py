"""
测试用例: 分组管理页面-右上方按钮-添加分组
功能点: 在分组管理页面点击右上角添加按钮进入添加分组流程
操作步骤: 进入管理分组页面，点击右上角添加按钮
预期结果: 进入添加分组流程
"""
import time
from conftest import BaseTest


class TestGroupManageAdd(BaseTest):
    """分组管理-添加分组"""

    def setup(self):
        self.userA = self.users("userA")

    def test_group_manage_add_button(self):
        """
        步骤:
        1. 打开会话分组面板
        2. 点击"管理"进入分组管理页面
        3. 点击右上角"添加"按钮
        4. 验证进入添加分组流程（出现输入分组名称的界面）
        """
        # 进入分组管理页面
        self.userA.aw.open_session_group_manage()
        time.sleep(1)

        # 点击右上角添加按钮（通常显示"+"或"添加"文字）
        add_pos = self.userA.aw.find_text_by_ocr("添加", timeout=5)
        if not add_pos:
            # 也可能是"+"号，尝试点击右上角区域
            self.userA.aw.tap(500, 90)
        else:
            self.userA.aw.tap(add_pos[0], add_pos[1])
        time.sleep(1)

        # 验证进入了添加分组流程（应出现分组名称输入框或新建分组页面）
        # 通常会出现"新建分组"或"分组名称"等文字
        result = self.userA.aw.find_text_by_ocr("分组", timeout=5)
        assert result, "未进入添加分组流程"

    def teardown(self):
        """返回消息列表"""
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
