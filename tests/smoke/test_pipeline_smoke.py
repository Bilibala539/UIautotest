"""
测试用例: 流水线链路冒烟

验证 平台用例 → 测试套 → 流水线 → pytest 执行 全链路连通性。
断言恒真,预期 100% 通过;失败即说明执行链路本身出了问题。
运行条件: PLATFORM=web(流水线配置平台选 Web,走浏览器,不依赖真机)。
"""
from conftest import BaseTest


class TestPipelineSmoke(BaseTest):
    """流水线链路冒烟测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户（无需 login，框架自动管理）
        - web 平台由框架启动浏览器会话,不占用真机
        """
        self.userA = self.users("userA")

    def test_pipeline_smoke(self):
        """
        测试场景: 链路连通性冒烟
        """
        assert 1 == 1

    def teardown(self):
        """
        测试后清理(无自定义清理)
        """
        pass
