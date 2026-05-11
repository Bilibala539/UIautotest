"""
测试用例: 群组活跃分组勾选（批量管理模态）
功能点: 在多选模态下勾选活跃分组下的群组
操作步骤: 进入多选模态，勾选活跃分组
预期结果: 可正常勾选整个分组下的群组
"""
import time
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="多选模态功能需要先进入批量管理入口，待探索确认入口路径后启用")
class TestBatchSelectActiveGroup(BaseTest):
    """群组活跃分组勾选"""

    def setup(self):
        self.userA = self.users("userA")

    def test_batch_select_active_group(self):
        """
        步骤:
        1. 进入分组详情页
        2. 进入多选模态（批量管理）
        3. 勾选活跃分组下的所有群组
        4. 验证勾选成功
        """
        # 需要先探索多选模态的入口
        pass

    def teardown(self):
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
