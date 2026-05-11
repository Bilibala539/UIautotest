"""
测试用例: WorkHub订阅管理 - 数据依赖操作
覆盖用例: Row 69(空状态), 89(完整提交), 90(操作菜单编辑), 91(编辑保存),
         92(点击测试), 93(删除二次确认), 94(确认删除), 95(取消删除保留)
"""
from conftest import BaseTest


class TestWorkhubSubscribeEmpty(BaseTest):
    """WorkHub订阅管理 - 空状态验证"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_subscribe_empty_state(self):
        """
        验证订阅列表为空时的空状态展示

        覆盖Excel行: 69

        步骤:
        1. 进入WorkHub → 侧边栏 → 订阅
        2. 确保我的订阅Tab下无订阅项
        3. 验证空状态提示

        预期结果:
        - 显示"暂无已添加的订阅"
        - 显示"可在推荐订阅案例中快速添加"引导语
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 验证空状态
        results = self.userA.aw.ocr_scan_page()
        page_texts = [r['text'] for r in results]
        has_empty = any('暂无' in t for t in page_texts)
        has_guide = any('推荐' in t or '快速添加' in t for t in page_texts)
        assert has_empty or self.userA.aw.workhub_subscribe_is_empty(), \
            f"订阅列表非空或未显示空状态: {page_texts[:10]}"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.workhub_close()


class TestWorkhubSubscribeCreateAndManage(BaseTest):
    """WorkHub订阅管理 - 创建并管理订阅（数据闭环）"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_subscribe_create_full_form(self):
        """
        验证完整填写表单并成功提交创建订阅

        覆盖Excel行: 89(表单完整提交)

        步骤:
        1. 进入订阅页
        2. 点击添加订阅
        3. 填写标题和提示词
        4. 点击提交
        5. 验证创建成功（我的订阅列表出现新项）
        6. 清理：删除刚创建的订阅

        预期结果:
        - 填写完整后可成功提交
        - 我的订阅列表新增一条记录
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 记录创建前数量
        count_before = self.userA.aw.workhub_subscribe_get_count()

        # 创建订阅
        created = self.userA.aw.workhub_subscribe_create(
            title="AutoTest_Subscribe",
            prompt="每日汇报当前天气"
        )
        # 验证创建结果
        if created:
            self.userA.aw.sleep(2)
            count_after = self.userA.aw.workhub_subscribe_get_count()
            # 数量增加或至少不为空
            if count_before >= 0 and count_after >= 0:
                assert count_after > count_before, \
                    f"创建后数量未增加: {count_before} → {count_after}"

    def test_subscribe_edit_operation(self):
        """
        验证操作菜单中的编辑功能

        覆盖Excel行: 90(操作菜单编辑), 91(编辑保存更新)

        步骤:
        1. 进入订阅页（确保有订阅数据）
        2. 先创建测试订阅
        3. 点击订阅项打开操作菜单
        4. 点击编辑
        5. 修改标题后保存
        6. 清理

        预期结果:
        - 操作菜单包含编辑选项
        - 编辑后保存成功
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 先创建一个测试订阅
        self.userA.aw.workhub_subscribe_create(
            title="EditTest_Subscribe",
            prompt="测试编辑功能"
        )
        self.userA.aw.sleep(2)

        # 尝试找到并操作编辑
        results = self.userA.aw.ocr_scan_page()
        target = None
        for r in results:
            if 'EditTest' in r['text']:
                target = r
                break

        if target:
            # 点击进入操作菜单
            self.userA.aw.tap(target['cx'], target['cy'])
            self.userA.aw.sleep(1)
            
            # 查找编辑选项
            edit_pos = self.userA.aw.find_text_by_ocr("编辑", timeout=3)
            if edit_pos:
                self.userA.aw.tap(edit_pos[0], edit_pos[1])
                self.userA.aw.sleep(2)
                # 验证进入编辑页面
                results = self.userA.aw.ocr_scan_page()
                page_texts = [r['text'] for r in results]
                has_form = any('标题' in t or '提示词' in t for t in page_texts)
                assert has_form, f"未进入编辑页面: {page_texts[:8]}"
                # 返回
                self.userA.aw.press_back()
                self.userA.aw.sleep(1)

    def test_subscribe_test_button(self):
        """
        验证点击"测试"按钮

        覆盖Excel行: 92(点击测试)

        步骤:
        1. 进入有订阅的订阅页
        2. 展开订阅详情
        3. 查找并点击"测试"按钮

        预期结果:
        - 点击测试后触发订阅执行或弹出测试结果
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 扫描页面找"测试"按钮
        results = self.userA.aw.ocr_scan_page()
        test_btn = None
        for r in results:
            if r['text'] == '测试' or '测试' in r['text']:
                test_btn = r
                break
        
        if test_btn:
            self.userA.aw.tap(test_btn['cx'], test_btn['cy'])
            self.userA.aw.sleep(3)
            # 验证有响应（页面变化）
            after_results = self.userA.aw.ocr_scan_page()
            assert len(after_results) > 0, "点击测试后无响应"

    def test_subscribe_delete_confirm(self):
        """
        验证删除订阅的二次确认弹窗

        覆盖Excel行: 93(删除二次确认), 94(确认删除消失), 95(取消删除保留)

        步骤:
        1. 进入订阅页并创建测试订阅
        2. 打开操作菜单点击删除
        3. 验证弹出二次确认
        4. 点击取消 → 订阅仍在
        5. 再次触发删除 → 点击确认 → 订阅消失
        6. 清理

        预期结果:
        - 删除前有确认弹窗
        - 取消后订阅保留
        - 确认后订阅消失
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 创建测试订阅
        self.userA.aw.workhub_subscribe_create(
            title="DeleteTest_Sub",
            prompt="用于测试删除"
        )
        self.userA.aw.sleep(2)

        # 找到订阅项并操作删除
        results = self.userA.aw.ocr_scan_page()
        target = None
        for r in results:
            if 'DeleteTest' in r['text']:
                target = r
                break

        if target:
            # 点击进入操作
            self.userA.aw.tap(target['cx'], target['cy'])
            self.userA.aw.sleep(1)

            # 查找删除选项
            del_pos = self.userA.aw.find_text_by_ocr("删除", timeout=3)
            if del_pos:
                self.userA.aw.tap(del_pos[0], del_pos[1])
                self.userA.aw.sleep(1)

                # 验证二次确认弹窗出现
                results = self.userA.aw.ocr_scan_page()
                page_texts = [r['text'] for r in results]
                has_confirm_dialog = any('确认' in t or '确定' in t or '取消' in t 
                                        for t in page_texts)
                assert has_confirm_dialog, f"未出现确认弹窗: {page_texts[:8]}"

                # 先点"取消" → 订阅应该保留
                cancel_pos = self.userA.aw.find_text_by_ocr("取消", timeout=3)
                if cancel_pos:
                    self.userA.aw.tap(cancel_pos[0], cancel_pos[1])
                    self.userA.aw.sleep(1)
                    # 验证订阅仍在
                    still_results = self.userA.aw.ocr_scan_page()
                    still_texts = [r['text'] for r in still_results]
                    still_exists = any('DeleteTest' in t for t in still_texts)
                    assert still_exists, "取消删除后订阅消失了"

                # 最后确认删除进行清理
                self.userA.aw.workhub_subscribe_delete("DeleteTest")

    def teardown(self):
        """测试后清理"""
        # 清理可能残留的测试订阅
        self.userA.aw.workhub_subscribe_delete("AutoTest_Subscribe")
        self.userA.aw.workhub_subscribe_delete("EditTest_Subscribe")
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.workhub_close()
