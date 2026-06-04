"""
测试用例: 空分组删除
功能点: 在分组管理页面删除一个空的分组
操作步骤: 进入管理分组页面，删除空分组
预期结果: 可以成功删除空分组
"""
import time
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="删除分组操作需要先创建测试分组，待探索分组创建流程后启用")
class TestDeleteEmptyGroup(BaseTest):
    """空分组删除"""

    def setup(self):
        self.userA = self.users("userA")

    def test_delete_empty_group(self):
        """
        步骤:
        1. 进入分组管理页面
        2. 进入编辑模式
        3. 找到一个空分组并点击删除按钮
        4. 确认删除
        5. 验证分组已从列表中移除
        """
        # 进入分组管理页面
        self.userA.aw.open_session_group_manage()
        time.sleep(1)

        # 进入编辑模式
        edit_pos = self.userA.aw.find_text_by_ocr("编辑", timeout=5)
        assert edit_pos, "未找到编辑按钮"
        self.userA.aw.tap(edit_pos[0], edit_pos[1])
        time.sleep(1)

        # 点击某个空分组的删除图标（通常是红色减号）
        # 这里需要先创建一个空分组，暂时跳过
        pass

    def teardown(self):
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
