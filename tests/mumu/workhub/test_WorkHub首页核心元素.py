"""
测试用例: WorkHub AI首页核心区域验证
验证加载完成后AI首页核心区域出现：标题、技能Tab、输入框、模型名称
"""
from conftest import BaseTest


class TestWorkhubHomeCoreArea(BaseTest):
    """WorkHub AI首页核心区域验证"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_workhub_home_core_elements(self):
        """
        验证WorkHub首页核心区域元素均存在
        
        步骤:
        1. 进入WorkHub
        2. 验证核心元素:
           - WorkHub标题
           - 技能Tab区（"通用"等Tab）
           - 输入框（"分配任务或提问"）
           - 模型名称（"Kimi K2.6"）
        
        预期结果:
        - 所有核心区域元素可见
        """
        # 进入WorkHub
        self.userA.aw.enter_workhub()

        # 验证WorkHub标题
        self.userA.aw.text_exists("WorkHub", timeout=5)

        # 验证欢迎文案
        self.userA.aw.text_exists("工作办事助手", timeout=5)

        # 验证技能Tab - "通用" Tab应该默认可见
        self.userA.aw.text_exists("通用", timeout=5)

        # 验证输入框
        self.userA.aw.text_exists("分配任务或提问", timeout=5)

        # 验证模型名称
        model_name = self.userA.aw.workhub_get_model_name()
        assert model_name != "", f"未找到模型名称，当前为空"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.workhub_close()
