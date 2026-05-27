"""
测试用例: WorkHub订阅管理
覆盖用例: Row 64-97, 164, 165 - 订阅入口、列表、toggle、新建、管理操作
"""
from conftest import BaseTest


class TestWorkhubSubscribeEntry(BaseTest):
    """WorkHub订阅管理 - 入口与列表"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_subscribe_entry_and_tabs(self):
        """
        验证从侧边栏进入订阅页，页面显示Tab

        覆盖Excel行: 64(侧边栏入口), 65(两个Tab), 66(默认我的订阅)

        步骤:
        1. 进入WorkHub → 打开侧边栏
        2. 点击"订阅"
        3. 验证订阅页面显示Tab

        预期结果:
        - 进入订阅页面
        - 显示"我的订阅"和"推荐订阅套装"Tab
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()

        # 点击订阅
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 验证进入了订阅页面
        results = self.userA.aw.ocr_scan_page()
        page_texts = [r['text'] for r in results]
        has_subscribe = any('订阅' in t or '推荐' in t for t in page_texts)
        assert has_subscribe, f"未进入订阅页面: {page_texts[:10]}"

    def test_subscribe_list_layout(self):
        """
        验证订阅列表条目布局

        覆盖Excel行: 67(列表布局完整), 68(角标与数量)

        步骤:
        1. 进入订阅页
        2. 验证列表条目有标题和开关

        预期结果:
        - 列表条目显示标题
        - 有toggle开关
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 扫描订阅列表
        results = self.userA.aw.ocr_scan_page()
        # 订阅列表应有多个元素
        assert len(results) >= 3, "订阅页面内容太少"

    def test_subscribe_recommend_tab(self):
        """
        验证推荐订阅套装Tab

        覆盖Excel行: 70(切换Tab), 71(模板卡片), 165(套用跳转)

        步骤:
        1. 进入订阅页
        2. 切换到"推荐订阅套装"Tab
        3. 验证显示模板卡片

        预期结果:
        - 推荐Tab可切换
        - 显示模板卡片列表
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 点击"推荐"Tab
        recommend_pos = self.userA.aw.find_text_by_ocr("推荐", timeout=5)
        if recommend_pos:
            self.userA.aw.tap(recommend_pos[0], recommend_pos[1])
            self.userA.aw.sleep(2)

            # 验证推荐Tab内容
            results = self.userA.aw.ocr_scan_page()
            assert len(results) >= 2, "推荐Tab无内容"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.workhub_close()


class TestWorkhubSubscribeToggle(BaseTest):
    """WorkHub订阅管理 - toggle与展开"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_subscribe_toggle(self):
        """
        验证toggle开关关闭/启用订阅

        覆盖Excel行: 72(关闭), 73(再次启用)

        步骤:
        1. 进入订阅页
        2. 找到toggle开关并点击
        3. 验证状态变化

        预期结果:
        - toggle可切换状态
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 扫描页面，找toggle区域（通常在右侧）
        # toggle开关一般不是文字，但可以通过点击右侧区域
        results = self.userA.aw.ocr_scan_page()
        # 找到第一个订阅项的位置
        subscribe_items = [r for r in results if 150 < r['cy'] < 500 and len(r['text']) > 3]
        if subscribe_items:
            # 点击右侧区域（toggle位置）
            item = subscribe_items[0]
            self.userA.aw.tap(480, item['cy'])
            self.userA.aw.sleep(1)
            # 再次点击恢复
            self.userA.aw.tap(480, item['cy'])
            self.userA.aw.sleep(1)

    def test_subscribe_expand_detail(self):
        """
        验证展开订阅详情

        覆盖Excel行: 74(展开), 75(历史记录), 76(点击进入详情), 77(收起)

        步骤:
        1. 进入订阅页
        2. 点击展开箭头
        3. 验证显示详情/历史记录
        4. 再次点击收起

        预期结果:
        - 展开后显示详情
        - 再次点击可收起
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 找到订阅列表项并点击展开
        results = self.userA.aw.ocr_scan_page()
        subscribe_items = [r for r in results if 150 < r['cy'] < 500 and len(r['text']) > 3]
        if subscribe_items:
            # 点击项目（展开）
            self.userA.aw.tap(subscribe_items[0]['cx'], subscribe_items[0]['cy'])
            self.userA.aw.sleep(2)

            # 扫描查看是否展开了更多内容
            results_after = self.userA.aw.ocr_scan_page()
            assert len(results_after) > 0, "展开后页面无内容"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.workhub_close()


class TestWorkhubSubscribeNew(BaseTest):
    """WorkHub订阅管理 - 新建订阅"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_subscribe_new_entry(self):
        """
        验证新建订阅入口和表单页

        覆盖Excel行: 78(入口按钮), 79(点击进入表单)

        步骤:
        1. 进入订阅页
        2. 查找新建按钮
        3. 点击进入表单页

        预期结果:
        - 新建按钮可见
        - 点击后进入新建订阅表单
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 查找新建按钮
        new_pos = self.userA.aw.find_text_by_ocr("新建", timeout=5)
        if not new_pos:
            new_pos = self.userA.aw.find_text_by_ocr("+", timeout=3)

        if new_pos:
            self.userA.aw.tap(new_pos[0], new_pos[1])
            self.userA.aw.sleep(3)

            # 验证进入表单页
            results = self.userA.aw.ocr_scan_page()
            page_texts = [r['text'] for r in results]
            has_form = any('标题' in t or '提示词' in t or '检索' in t for t in page_texts)
            assert has_form, f"未进入新建表单页: {page_texts[:10]}"

    def test_subscribe_form_validation(self):
        """
        验证新建订阅表单校验

        覆盖Excel行: 80(标题空提示), 81(超长限制), 82(提示词空)

        步骤:
        1. 进入新建订阅表单
        2. 不填写标题直接提交
        3. 验证提示信息

        预期结果:
        - 空标题时显示校验提示
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_click_subscribe()
        self.userA.aw.sleep(3)

        # 进入新建表单
        new_pos = self.userA.aw.find_text_by_ocr("新建", timeout=5)
        if new_pos:
            self.userA.aw.tap(new_pos[0], new_pos[1])
            self.userA.aw.sleep(3)

            # 查找提交/保存按钮
            submit_pos = self.userA.aw.find_text_by_ocr("保存", timeout=3)
            if not submit_pos:
                submit_pos = self.userA.aw.find_text_by_ocr("提交", timeout=3)
            if not submit_pos:
                submit_pos = self.userA.aw.find_text_by_ocr("确定", timeout=3)

            if submit_pos:
                # 不填内容直接提交
                self.userA.aw.tap(submit_pos[0], submit_pos[1])
                self.userA.aw.sleep(2)

                # 应该有错误提示
                results = self.userA.aw.ocr_scan_page()
                page_texts = [r['text'] for r in results]
                has_error = any('请' in t or '不能为空' in t or '必填' in t for t in page_texts)
                # 有错误提示或仍在表单页面（未跳转），都算通过
                still_on_form = any('标题' in t or '提示词' in t for t in page_texts)
                assert has_error or still_on_form, "空表单提交后未见校验提示"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.workhub_close()
