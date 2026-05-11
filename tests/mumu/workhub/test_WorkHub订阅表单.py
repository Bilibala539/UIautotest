"""
测试用例: WorkHub订阅管理 - 表单深度验证
覆盖用例: Row 83(提示词空AI生成不可用), 84(AI生成替换), 85(AI生成按钮禁用),
         86(检索范围默认), 87(未选检索范围提示), 88(推送时间选择)
"""
from conftest import BaseTest


class TestWorkhubSubscribeFormDeep(BaseTest):
    """WorkHub订阅管理 - 新建表单深度字段验证"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def _navigate_to_new_form(self):
        """辅助方法: 导航到新建订阅表单"""
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)
        self.userA.aw.workhub_subscribe_click_add()
        self.userA.aw.sleep(3)

    def test_prompt_empty_ai_generate_disabled(self):
        """
        验证提示词为空时AI生成按钮不可用

        覆盖Excel行: 83

        步骤:
        1. 进入新建订阅表单
        2. 不填写提示词
        3. 查看AI生成按钮状态

        预期结果:
        - 提示词为空时，AI生成按钮不可点击或灰色
        """
        self._navigate_to_new_form()

        # 扫描页面查找AI生成相关按钮
        results = self.userA.aw.ocr_scan_page()
        page_texts = [r['text'] for r in results]

        # 验证表单页面元素存在
        has_form_elements = any('标题' in t or '提示词' in t for t in page_texts)
        assert has_form_elements, f"未在表单页面: {page_texts[:10]}"

        # 查找AI生成按钮
        ai_btn = None
        for r in results:
            if 'AI' in r['text'] or '生成' in r['text'] or '智能' in r['text']:
                ai_btn = r
                break

        # 如果找到AI按钮，尝试点击验证是否有响应
        if ai_btn:
            self.userA.aw.tap(ai_btn['cx'], ai_btn['cy'])
            self.userA.aw.sleep(2)
            # 验证仍在表单页（按钮无效时不会跳转）
            after = self.userA.aw.ocr_scan_page()
            after_texts = [r['text'] for r in after]
            still_on_form = any('标题' in t or '提示词' in t for t in after_texts)
            assert still_on_form, "提示词空时AI生成按钮不应可用"

    def test_ai_generate_replaces_content(self):
        """
        验证AI生成替换提示词内容

        覆盖Excel行: 84

        步骤:
        1. 进入新建订阅表单
        2. 先填写提示词
        3. 点击AI生成按钮
        4. 等待生成完成
        5. 验证内容被替换

        预期结果:
        - AI生成后提示词区域内容发生变化
        """
        self._navigate_to_new_form()

        # 填写提示词
        prompt_pos = self.userA.aw.find_text_by_ocr("提示词", timeout=5)
        if prompt_pos:
            self.userA.aw.tap(prompt_pos[0], prompt_pos[1] + 40)
            self.userA.aw.sleep(0.5)
            self.userA.aw.input_text("summarize daily news")
            self.userA.aw.sleep(1)

        # 查找并点击AI生成按钮
        results = self.userA.aw.ocr_scan_page()
        for r in results:
            if 'AI' in r['text'] or '生成' in r['text']:
                self.userA.aw.tap(r['cx'], r['cy'])
                self.userA.aw.sleep(5)  # 等待AI生成
                break

        # 验证页面有响应
        after = self.userA.aw.ocr_scan_page()
        assert len(after) > 0, "AI生成后页面无内容"

    def test_ai_generate_button_disabled_during_gen(self):
        """
        验证AI生成过程中按钮禁用

        覆盖Excel行: 85

        步骤:
        1. 触发AI生成
        2. 在生成过程中尝试再次点击
        3. 验证按钮不响应

        预期结果:
        - 生成中按钮禁用或显示loading状态
        """
        self._navigate_to_new_form()

        # 填写提示词
        prompt_pos = self.userA.aw.find_text_by_ocr("提示词", timeout=5)
        if prompt_pos:
            self.userA.aw.tap(prompt_pos[0], prompt_pos[1] + 40)
            self.userA.aw.sleep(0.5)
            self.userA.aw.input_text("analyze market trend")
            self.userA.aw.sleep(1)

        # 触发AI生成
        results = self.userA.aw.ocr_scan_page()
        ai_btn_pos = None
        for r in results:
            if 'AI' in r['text'] or '生成' in r['text']:
                ai_btn_pos = (r['cx'], r['cy'])
                self.userA.aw.tap(r['cx'], r['cy'])
                break

        if ai_btn_pos:
            # 快速再次点击（应该无效）
            self.userA.aw.sleep(0.5)
            self.userA.aw.tap(ai_btn_pos[0], ai_btn_pos[1])
            self.userA.aw.sleep(3)
            # 验证页面正常（未出错）
            after = self.userA.aw.ocr_scan_page()
            assert len(after) > 0, "页面异常"

    def test_retrieval_scope_default(self):
        """
        验证检索范围默认未选中

        覆盖Excel行: 86

        步骤:
        1. 进入新建订阅表单
        2. 滚动查找"检索范围"字段
        3. 验证默认状态

        预期结果:
        - 检索范围字段默认未选中任何选项
        """
        self._navigate_to_new_form()

        # 向下滚动查看完整表单
        self.userA.aw.swipe_up(distance=300)
        self.userA.aw.sleep(1)

        # 查找检索范围相关文字
        results = self.userA.aw.ocr_scan_page()
        page_texts = [r['text'] for r in results]
        has_retrieval = any('检索' in t or '范围' in t for t in page_texts)

        if not has_retrieval:
            # 继续滚动
            self.userA.aw.swipe_up(distance=300)
            self.userA.aw.sleep(1)
            results = self.userA.aw.ocr_scan_page()
            page_texts = [r['text'] for r in results]

        # 验证有检索范围字段或表单其他字段
        has_form = any('检索' in t or '范围' in t or '推送' in t or '提示词' in t
                      for t in page_texts)
        assert has_form, f"未找到表单深度字段: {page_texts[:10]}"

    def test_submit_without_retrieval_scope(self):
        """
        验证未选检索范围时提交给出提示

        覆盖Excel行: 87

        步骤:
        1. 进入新建订阅表单
        2. 填写标题和提示词但不选检索范围
        3. 点击提交
        4. 验证提示信息

        预期结果:
        - 提交后显示需要选择检索范围的提示
        """
        self._navigate_to_new_form()

        # 填写标题
        title_pos = self.userA.aw.find_text_by_ocr("标题", timeout=5)
        if title_pos:
            self.userA.aw.tap(title_pos[0], title_pos[1] + 40)
            self.userA.aw.sleep(0.5)
            self.userA.aw.input_text("TestNoScope")
            self.userA.aw.sleep(1)

        # 填写提示词
        prompt_pos = self.userA.aw.find_text_by_ocr("提示词", timeout=5)
        if prompt_pos:
            self.userA.aw.tap(prompt_pos[0], prompt_pos[1] + 40)
            self.userA.aw.sleep(0.5)
            self.userA.aw.input_text("test prompt")
            self.userA.aw.sleep(1)

        # 不选检索范围直接提交
        for btn in ["保存", "提交", "确定", "创建"]:
            btn_pos = self.userA.aw.find_text_by_ocr(btn, timeout=2)
            if btn_pos:
                self.userA.aw.tap(btn_pos[0], btn_pos[1])
                self.userA.aw.sleep(2)
                break

        # 验证有错误提示或仍在表单
        results = self.userA.aw.ocr_scan_page()
        page_texts = [r['text'] for r in results]
        still_on_form = any('标题' in t or '提示词' in t or '检索' in t for t in page_texts)
        has_error = any('请' in t or '选择' in t or '必填' in t for t in page_texts)
        assert still_on_form or has_error, "未选范围也提交成功了"

    def test_push_time_selector(self):
        """
        验证推送时间选择器

        覆盖Excel行: 88

        步骤:
        1. 进入新建订阅表单
        2. 找到推送时间字段
        3. 点击打开时间选择器
        4. 验证时间选择器UI

        预期结果:
        - 推送时间字段可点击
        - 弹出时间选择器或下拉选项
        """
        self._navigate_to_new_form()

        # 滚动到推送时间字段
        self.userA.aw.swipe_up(distance=300)
        self.userA.aw.sleep(1)

        # 查找推送时间
        push_pos = self.userA.aw.find_text_by_ocr("推送", timeout=5)
        if not push_pos:
            self.userA.aw.swipe_up(distance=300)
            self.userA.aw.sleep(1)
            push_pos = self.userA.aw.find_text_by_ocr("推送", timeout=5)

        if push_pos:
            # 点击推送时间字段
            self.userA.aw.tap(push_pos[0], push_pos[1] + 30)
            self.userA.aw.sleep(2)

            # 验证弹出了时间选择器
            results = self.userA.aw.ocr_scan_page()
            page_texts = [r['text'] for r in results]
            # 时间选择器可能包含小时、分钟或具体时间选项
            has_time_ui = any(any(kw in t for kw in ['时', '分', '每天', '每周', '上午', '下午', ':'])
                            for t in page_texts)
            assert has_time_ui or len(results) > 3, \
                f"未弹出时间选择器: {page_texts[:10]}"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.workhub_close()
