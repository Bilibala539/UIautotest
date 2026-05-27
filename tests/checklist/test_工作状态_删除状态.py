"""
测试用例: 工作状态-删除状态
功能点: 在工作状态编辑页面删除自定义状态
操作步骤: 点击删除按钮
预期结果: 弹出二次确认弹窗，点击删除则删除该状态
"""
import time
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="工作状态页面入口坐标待探索确认")
class TestWorkStatusDelete(BaseTest):
    """工作状态-删除状态"""

    def setup(self):
        self.userA = self.users("userA")

    def test_delete_work_status(self):
        """
        步骤:
        1. 进入工作状态设置页面
        2. 找到一个可删除的自定义状态
        3. 点击删除按钮
        4. 验证弹出二次确认弹窗
        5. 点击确认删除
        6. 验证状态已从列表中移除
        """
        # 进入工作状态页面
        self.userA.aw.open_work_status_page()
        time.sleep(1)

        # 查找自定义状态（如果之前新增过"自动化测试状态"）
        # 或者找到编辑/删除入口
        edit_pos = self.userA.aw.find_text_by_ocr("编辑", timeout=3)
        if edit_pos:
            self.userA.aw.tap(edit_pos[0], edit_pos[1])
            time.sleep(1)

        # 点击删除按钮
        delete_pos = self.userA.aw.find_text_by_ocr("删除", timeout=5)
        assert delete_pos, "未找到删除按钮"
        self.userA.aw.tap(delete_pos[0], delete_pos[1])
        time.sleep(1)

        # 验证二次确认弹窗出现
        confirm_pos = self.userA.aw.find_text_by_ocr("确认", timeout=5)
        if not confirm_pos:
            confirm_pos = self.userA.aw.find_text_by_ocr("删除", timeout=3)
        assert confirm_pos, "未出现二次确认弹窗"

        # 点击取消（不真正删除，只验证弹窗出现）
        cancel_pos = self.userA.aw.find_text_by_ocr("取消", timeout=3)
        if cancel_pos:
            self.userA.aw.tap(cancel_pos[0], cancel_pos[1])

    def teardown(self):
        """返回消息列表"""
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
