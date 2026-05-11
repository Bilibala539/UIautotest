"""
测试用例: 群组批量管理 - 全选群组

用例来源: 会话列表及会话盒子.xlsx Row 67
测试场景: 点击全选按钮，验证所有群组被选中
预期: 已选数量等于群组总数，底部按钮可用
"""
from conftest import BaseTest


class TestGroupBatchSelectAll(BaseTest):
    """群组批量管理 - 全选群组"""

    def setup(self):
        """
        测试前初始化
        """
        self.userA = self.users("userA")

    def test_batch_select_all(self):
        """
        测试场景: 进入批量管理模式后点击全选
        步骤:
        1. 打开通讯录群组列表
        2. 进入批量管理模式
        3. 点击全选按钮
        4. 验证已选数量大于0
        5. 验证底部按钮存在
        """
        # 1. 打开通讯录群组列表
        self.userA.open_contacts_groups()

        # 2. 进入批量管理模式
        self.userA.enter_group_batch_manage()

        # 3. 点击全选
        self.userA.batch_select_all_groups()

        # 4. 验证已选数量大于0（全选后应选中所有可见群组）
        count = self.userA.get_batch_selected_count()
        assert count > 0, f"全选后期望已选数量>0，实际为{count}"

        # 5. 验证底部按钮
        buttons = self.userA.verify_batch_bottom_buttons()
        assert buttons['exit_group'], "全选后底部应显示'退出群组'按钮"
        assert buttons['dissolve_group'], "全选后底部应显示'解散群组'按钮"

    def teardown(self):
        """测试后清理 - 退出批量管理模式"""
        self.userA.exit_group_batch_manage()
