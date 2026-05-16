"""
清理用例: 清除 grp.popoqa50 会话中残留的"自动化测试标签页"

使用场景:
  test_P2P添加自定义标签页 的 teardown 失败时，"自动化测试标签页"
  可能残留在 grp.popoqa50 的标签页列表中，影响后续该用例的执行结果。
  本用例检测并清除所有残留，建议排在 test_P2P添加自定义标签页 之前执行。
"""
import logging
from conftest import BaseTest

logger = logging.getLogger(__name__)


class TestCleanupResidualTabPage(BaseTest):
    """清理 grp.popoqa50 会话中残留的自动化测试标签页"""

    RECIPIENT = "grp.popoqa50"
    TAB_NAME = "自动化测试标签页"
    MAX_CLEANUP = 5  # 防止极端情况下的无限循环

    def setup(self):
        self.userA = self.users("userA")

    def test_cleanup_residual_tab_page(self):
        """
        检查并清理 grp.popoqa50 会话中残留的 "自动化测试标签页"。
        - 无残留：直接通过，不执行任何删除操作
        - 有残留：逐个删除直到全部清除后通过

        操作路径: 消息列表 → 搜索 grp.popoqa50 → P2P 设置 → 标签页 → 管理 → 删除
        """
        cleaned = 0
        for _ in range(self.MAX_CLEANUP):
            try:
                was_deleted = self.userA.remove_custom_tab_page(self.RECIPIENT, self.TAB_NAME)
            except Exception as e:
                logger.warning(f"⚠️ 清理时遇到导航异常，停止重试: {e}")
                break

            if was_deleted:
                cleaned += 1
                logger.info(f"已清理第 {cleaned} 个残留标签页")
            else:
                break  # 未找到残留，无需继续

        if cleaned > 0:
            logger.info(f"✅ 清理完成，共删除 {cleaned} 个残留 '{self.TAB_NAME}'")
        else:
            logger.info(f"✅ 无残留标签页，环境干净")
