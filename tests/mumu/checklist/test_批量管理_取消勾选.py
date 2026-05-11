"""
测试用例: 群组批量管理 - 取消退出多选模态

用例来源: 会话列表及会话盒子.xlsx Row 69
测试场景: 在批量管理模式中点击取消，验证退出多选模态
预期: 退出批量管理模式，恢复正常群组列表视图
"""
from conftest import BaseTest


class TestGroupBatchCancel(BaseTest):
    """群组批量管理 - 取消退出"""

    def setup(self):
        """
        测试前初始化
        """
        self.userA = self.users("userA")

    def test_batch_cancel(self):
        """
        测试场景: 进入批量管理模式后点击取消退出
        步骤:
        1. 打开通讯录群组列表
        2. 进入批量管理模式
        3. 验证已进入（看到"已选"文字）
        4. 点击取消退出
        5. 验证已回到正常群组列表（看到"批量管理"按钮）
        """
        # 1. 打开通讯录群组列表
        self.userA.open_contacts_groups()

        # 2. 进入批量管理模式
        self.userA.enter_group_batch_manage()

        # 3. 验证已进入
        count = self.userA.get_batch_selected_count()
        assert count == 0, f"初始状态应为0个选中，实际为{count}个"

        # 4. 退出批量管理模式
        self.userA.exit_group_batch_manage()

        # 5. 验证已回到正常群组列表 - find_text会在exit方法中验证

    def teardown(self):
        """测试后清理"""
        pass
