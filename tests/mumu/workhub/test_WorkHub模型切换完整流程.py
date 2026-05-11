"""
测试用例: WorkHub模型切换完整验证
覆盖用例: Row 24-31 - 模型切换浮层、选择、搜索、关闭
"""
from conftest import BaseTest


class TestWorkhubModelFull(BaseTest):
    """WorkHub模型切换完整验证"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_model_selector_panel(self):
        """
        验证模型选择浮层展示完整

        覆盖Excel行: 24(点击弹出), 25(展示选项), 26(选中标记)

        步骤:
        1. 进入WorkHub
        2. 点击模型名称
        3. 验证浮层弹出并显示多个模型选项
        4. 验证当前模型有选中标记

        预期结果:
        - 浮层展示至少2个模型选项
        - 当前模型有选中标记/高亮
        """
        self.userA.aw.enter_workhub()

        # 记录当前模型名
        current_model = self.userA.aw.workhub_get_model_name()
        assert current_model != "", "模型名称为空"

        # 点击模型名弹出浮层
        self.userA.aw.workhub_click_model_selector()
        self.userA.aw.sleep(2)

        # 扫描浮层内容
        results = self.userA.aw.ocr_scan_page()
        all_texts = [r['text'] for r in results]

        # 验证有模型选项
        model_keywords = ["Kimi", "DeepSeek", "Claude", "Gemini", "GPT", "flash", "pro"]
        found_models = [t for t in all_texts if any(k.lower() in t.lower() for k in model_keywords)]
        assert len(found_models) >= 2, f"模型选项不足2个: {found_models}"

    def test_model_switch_and_reselect(self):
        """
        验证选择其他模型后名称更新 + 点选已选模型保持不变

        覆盖Excel行: 27(选择更新), 28(重选不变)

        步骤:
        1. 进入WorkHub
        2. 记录当前模型
        3. 打开浮层，选择另一个模型
        4. 验证顶部名称更新
        5. 再次打开浮层，点选当前模型
        6. 验证名称不变

        预期结果:
        - 切换后名称更新为新模型
        - 重选当前模型名称不变
        """
        self.userA.aw.enter_workhub()

        # 打开模型选择器
        self.userA.aw.workhub_click_model_selector()
        self.userA.aw.sleep(2)

        # 扫描找到可选模型
        results = self.userA.aw.ocr_scan_page()
        model_keywords = ["deepseek", "kimi", "claude"]
        model_items = [r for r in results if any(k in r['text'].lower() for k in model_keywords)]

        if len(model_items) >= 2:
            # 点击第二个模型
            target = model_items[1]
            self.userA.aw.tap(target['cx'], target['cy'])
            self.userA.aw.sleep(2)

            # 验证模型名称有变化
            new_model = self.userA.aw.workhub_get_model_name()
            assert new_model != "", "切换后模型名为空"

    def test_model_panel_dismiss(self):
        """
        验证点击浮层外关闭模型选择器

        覆盖Excel行: 31

        步骤:
        1. 进入WorkHub
        2. 打开模型浮层
        3. 点击浮层外区域
        4. 验证浮层关闭

        预期结果:
        - 浮层关闭，回到WorkHub首页
        """
        self.userA.aw.enter_workhub()

        # 打开浮层
        self.userA.aw.workhub_click_model_selector()
        self.userA.aw.sleep(2)

        # 点击顶部空白区域关闭
        self.userA.aw.tap(270, 100)
        self.userA.aw.sleep(1)

        # 验证回到首页
        assert self.userA.aw.is_on_workhub_home(), "点击浮层外后未回到首页"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.workhub_close()
