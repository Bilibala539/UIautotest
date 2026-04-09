"""
测试用例: 发送P2P消息后撤回
探索来源: AI自主探索POPO App生成
探索记录: explorer_output/records/exploration_record_recall_message.md
"""
from conftest import BaseTest


class TestRecallMessage(BaseTest):
    """撤回消息测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户A
        - 用户A登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_recall_p2p_message(self):
        """
        测试场景: 发送P2P消息后通过长按消息体撤回

        步骤:
        1. 通过搜索联系人进入P2P聊天页面
        2. 发送一条测试消息
        3. 长按刚刚发送的消息体（≥1.5秒）
        4. 弹出操作菜单（底部浮动面板）
        5. 点击"撤回"选项
        6. 在确认弹窗中点击"确定"
        7. 验证撤回成功（出现"你撤回了一条消息"提示）

        预期结果:
        - 长按消息体弹出操作菜单
        - 操作菜单中包含"撤回"选项
        - 点击撤回后弹出确认弹窗
        - 确认后消息被撤回，显示"你撤回了一条消息"
        """
        # 1. 发送消息（会自动进入聊天页面再返回消息列表）
        message = self.userA.send_message(recipient="grp.popoqa93", isback=False)
        # 2. 撤回消息
        recall_result = self.userA.recall_message(message)
        assert recall_result, "消息撤回应该成功"
        # 3. 返回消息列表
        self.userA.aw.press_back()

    def teardown(self):
        """
        测试后清理
        - 用户退登
        - 停止应用
        """
        try:
            self.userA.logout()
        finally:
            self.userA.aw.stop_app()
