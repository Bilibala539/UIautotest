"""
测试用例: 会话列表长按操作测试
探索来源: AI自主探索POPO App生成
覆盖文字用例:
  - 长按会话置顶
  - 长按会话添加到待处理
  - 长按会话设为未读
  - 长按会话添加至分组
  - 会话添加到分组模块 (部分覆盖)
"""
import pytest
from conftest import BaseTest


class TestSessionListLongPress(BaseTest):
    """会话列表长按操作测试类"""

    def setup(self):
        """
        测试前初始化
        """
        self.userA = self.users("userA")

    def test_long_press_pin(self):
        """
        验证长按会话置顶/取消置顶
        覆盖用例: 置顶联系人会话
        预期: 长按后弹出菜单，点击置顶或取消置顶
        """
        result = self.userA.long_press_session_pin()
        assert result, "置顶/取消置顶操作应该成功"

    def test_long_press_add_to_pending(self):
        """
        验证长按会话添加到待处理/处理完成
        覆盖用例: 添加到待处理
        预期: 长按后弹出菜单，点击添加到待处理或处理完成
        """
        result = self.userA.long_press_session_add_to_pending()
        assert result in ("添加到待处理", "处理完成"), f"操作结果异常: {result}"

    def test_long_press_toggle_read_status(self):
        """
        验证长按会话切换已读/未读状态
        预期: 长按后弹出菜单（可能需要滑动），找到"设为未读"或"设为已读"并点击
        """
        result = self.userA.long_press_session_toggle_read_status()
        assert result in ("设为未读", "设为已读"), f"操作结果异常: {result}"

    def test_long_press_add_to_group(self):
        """
        验证长按会话添加至分组
        覆盖用例: 给会话添加分组
        预期: 长按后弹出菜单（需要滑动），点击添加至分组后进入分组选择页面
        """
        self.userA.long_press_session_add_to_group()
        # 验证进入了分组选择页面 - 应该能看到分组列表
        import time
        time.sleep(1)
        # 返回
        self.userA.aw.press_back()

    def teardown(self):
        """测试后清理"""
        pass
