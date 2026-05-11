"""
测试用例: WorkHub模型选择器验证
验证底部模型名称显示正确，点击可弹出模型切换浮层
"""
from conftest import BaseTest


class TestWorkhubModelSelector(BaseTest):
    """WorkHub模型选择器验证"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_model_name_visible(self):
        """
        验证WorkHub首页底部显示当前模型名称
        
        步骤:
        1. 进入WorkHub
        2. 检查底部是否显示模型名称（如"Kimi K2.6"）
        
        预期结果:
        - 模型名称可见且非空
        """
        self.userA.aw.enter_workhub()

        # 获取模型名称
        model_name = self.userA.aw.workhub_get_model_name()
        assert model_name != "", "底部未显示模型名称"
        assert "Kimi" in model_name or "Claude" in model_name or "DeepSeek" in model_name, \
            f"模型名称不符合预期: {model_name}"

    def test_click_model_opens_selector(self):
        """
        验证点击模型名称可以弹出模型切换浮层
        
        步骤:
        1. 进入WorkHub
        2. 点击底部模型名称
        3. 验证弹出模型切换浮层
        
        预期结果:
        - 弹出模型选择浮层，可见多个模型选项
        """
        self.userA.aw.enter_workhub()

        # 点击模型名称
        result = self.userA.aw.workhub_click_model_selector()
        assert result, "未能点击模型名称"

        # 验证弹出了模型选择浮层 - 应该能看到其他模型名字
        self.userA.aw.sleep(2)
        # 浮层中应该有模型列表
        results = self.userA.aw.ocr_scan_page()
        model_keywords = ["Kimi", "Claude", "DeepSeek", "Gemini", "GPT"]
        found_models = [r['text'] for r in results if any(k in r['text'] for k in model_keywords)]
        assert len(found_models) >= 1, "模型选择浮层未弹出或未找到模型选项"

    def teardown(self):
        """测试后清理"""
        # 按返回关闭可能的浮层
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.workhub_close()
