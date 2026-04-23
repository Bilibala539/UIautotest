"""
测试用例: 创建日历本
探索来源: AI自主探索POPO App日历功能生成
"""
import logging
from conftest import BaseTest

logger = logging.getLogger(__name__)


class TestCreateCalendarBook(BaseTest):
    """创建日历本测试类"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_create_calendar_book(self):
        """
        测试创建日历本

        步骤:
        1. 展开日历侧边栏
        2. 点击搜索框右侧+号
        3. 创建日历本

        预期结果:
        可以正常创建日历本，并展示在侧边栏
        """
        result = self.userA.create_calendar_book("AutoTestCal")
        assert result, "创建日历本应该成功"

    def teardown(self):
        """测试后清理 - 删除创建的日历本"""
        try:
            self.userA.delete_calendar_book("AutoTestCal")
        except Exception as e:
            logger.warning(f"⚠️ teardown 清理失败（不影响测试结果）: {e}")
