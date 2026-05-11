"""
测试用例: 分组管理页面-右上方按钮-设置
功能点: 在分组管理页面点击右上角设置按钮进入管理分组流程
操作步骤: 进入管理分组页面，点击右上角设置按钮
预期结果: 进入管理分组流程（编辑、排序等）
"""
import time
from conftest import BaseTest


class TestGroupManageSettings(BaseTest):
    """分组管理-设置按钮"""

    def setup(self):
        self.userA = self.users("userA")

    def test_group_manage_settings_button(self):
        """
        步骤:
        1. 打开会话分组面板
        2. 点击"管理"进入分组管理页面
        3. 点击右上角"设置"或"编辑"按钮
        4. 验证进入编辑模式（显示删除/拖动排序等选项）
        """
        # 进入分组管理页面
        self.userA.aw.open_session_group_manage()
        time.sleep(1)

        # 点击设置/编辑按钮
        edit_pos = self.userA.aw.find_text_by_ocr("编辑", timeout=3)
        if not edit_pos:
            edit_pos = self.userA.aw.find_text_by_ocr("设置", timeout=3)
        assert edit_pos, "分组管理页面未找到'编辑'或'设置'按钮"
        self.userA.aw.tap(edit_pos[0], edit_pos[1])
        time.sleep(1)

        # 验证进入编辑模式（通常会出现"完成"按钮或删除图标）
        done_pos = self.userA.aw.find_text_by_ocr("完成", timeout=5)
        assert done_pos, "未进入编辑/设置模式"

        # 退出编辑模式
        self.userA.aw.tap(done_pos[0], done_pos[1])

    def teardown(self):
        """返回消息列表"""
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
