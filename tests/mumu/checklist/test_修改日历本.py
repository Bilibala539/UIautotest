"""
测试用例: 修改日历本
探索来源: AI自主探索POPO App日历功能生成
"""
import time
import logging
from conftest import BaseTest

logger = logging.getLogger(__name__)


class TestModifyCalendarBook(BaseTest):
    """修改日历本测试类"""

    def setup(self):
        """测试前初始化 - 先创建一个日历本用于修改"""
        self.userA = self.users("userA")
        # 使用时间戳后缀确保名称唯一，避免与历史脏数据冲突
        ts = str(int(time.time()))[-4:]
        self.original_name = f"Mfy{ts}"
        self.new_name = f"Mfd{ts}"
        self.userA.create_calendar_book(self.original_name)

    def test_modify_calendar_book(self):
        """
        测试修改日历本

        步骤:
        1. 展开日历侧边栏
        2. 点击日历本右侧...按钮
        3. 点击日历设置，修改日历本名称

        预期结果:
        可以正常修改日历本
        """
        result = self.userA.modify_calendar_book(self.original_name, self.new_name)
        assert result, "修改日历本应该成功"

    def teardown(self):
        """测试后清理 - 删除修改后的日历本"""
        try:
            self.userA.delete_calendar_book(self.new_name)
        except Exception as e:
            logger.warning(f"⚠️ teardown 清理失败（不影响测试结果）: {e}")
