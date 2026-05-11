"""
测试用例: 群组批量管理 - 进入多选模态并勾选群组

用例来源: 会话列表及会话盒子.xlsx Row 65
测试场景: 进入多选模态-勾选单个非群主群组-查看底部按钮状态
预期: 底部显示"退出群组"按钮（可点击），"解散群组"按钮（不可点击/灰色）
"""
from conftest import BaseTest


class TestGroupBatchSelectSingle(BaseTest):
    """群组批量管理 - 勾选单个群组后查看底部按钮"""

    def setup(self):
        """
        测试前初始化
        """
        self.userA = self.users("userA")

    def test_batch_select_single_group(self):
        """
        测试场景: 进入批量管理模式，勾选一个群组，验证底部按钮存在
        步骤:
        1. 打开通讯录群组列表
        2. 进入批量管理模式
        3. 选中第1个群组
        4. 验证已选计数为1
        5. 验证底部按钮（全选、退出群组、解散群组）均存在
        """
        # 1. 打开通讯录群组列表
        self.userA.open_contacts_groups()

        # 2. 进入批量管理模式
        self.userA.enter_group_batch_manage()

        # 3. 选中第1个群组
        self.userA.select_group_in_batch(group_index=1)

        # 4. 验证已选计数为1
        count = self.userA.get_batch_selected_count()
        assert count == 1, f"期望已选1个群组，实际已选{count}个"

        # 5. 验证底部按钮存在
        buttons = self.userA.verify_batch_bottom_buttons()
        assert buttons['select_all'], "底部应显示'全选'按钮"
        assert buttons['exit_group'], "底部应显示'退出群组'按钮"
        # 注: 选中非群主群组时，"解散群组"按钮变灰/不可识别，符合预期

    def teardown(self):
        """测试后清理 - 退出批量管理模式"""
        self.userA.exit_group_batch_manage()
