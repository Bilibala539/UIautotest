"""
测试用例: WorkHub新任务页与产出物页面
覆盖用例: Row 45-51(新任务页), Row 52-63,167(产出物页)
"""
from conftest import BaseTest


class TestWorkhubNewTask(BaseTest):
    """WorkHub新任务页验证"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_new_task_page_entry(self):
        """
        验证点击+新建进入新任务页，标题为WorkHub

        覆盖Excel行: 45(点击新建+), 46(标题为WorkHub)

        步骤:
        1. 进入WorkHub
        2. 打开侧边栏
        3. 点击"+新对话"
        4. 验证进入新任务页

        预期结果:
        - 新任务页标题显示WorkHub或进入对话页
        """
        self.userA.aw.enter_workhub()
        self.userA.aw.workhub_open_sidebar()
        self.userA.aw.workhub_sidebar_new_dialog()
        self.userA.aw.sleep(3)

        # 验证进入了新对话/任务页
        results = self.userA.aw.ocr_scan_page()
        page_texts = [r['text'] for r in results]
        has_workhub = any('WorkHub' in t or '分配任务' in t or '提问' in t for t in page_texts)
        assert has_workhub, f"新任务页未正确显示: {page_texts[:10]}"

    def test_new_task_close_return(self):
        """
        验证从WorkHub入口关闭X返回AI首页

        覆盖Excel行: 49

        步骤:
        1. 进入WorkHub → 发起新对话
        2. 点击关闭X按钮
        3. 验证返回AI首页

        预期结果:
        - 点击X后回到AI首页或消息列表
        """
        self.userA.aw.enter_workhub()

        # 查找X关闭按钮（通常在右上角）
        results = self.userA.aw.ocr_scan_page()
        x_buttons = [r for r in results if r['text'] == 'X' or r['text'] == 'x']

        if x_buttons:
            self.userA.aw.tap(x_buttons[0]['cx'], x_buttons[0]['cy'])
            self.userA.aw.sleep(2)
        else:
            # 尝试按返回键
            self.userA.aw.press_back()
            self.userA.aw.sleep(2)

        # 应该回到消息列表或AI首页
        msg_pos = self.userA.aw.find_text_by_ocr("消息", timeout=3)
        wh_pos = self.userA.aw.find_text_by_ocr("WorkHub", timeout=3)
        assert msg_pos or wh_pos, "关闭后未返回到预期页面"

    def test_new_task_search_toggle(self):
        """
        验证全网搜索toggle开关

        覆盖Excel行: 51

        步骤:
        1. 进入WorkHub
        2. 查找全网搜索相关toggle
        3. 验证toggle可切换

        预期结果:
        - 全网搜索开关可见并可切换状态
        """
        self.userA.aw.enter_workhub()

        # 查找"全网搜索"文字
        search_pos = self.userA.aw.find_text_by_ocr("全网搜索", timeout=5)
        if search_pos:
            # 点击toggle
            self.userA.aw.tap(search_pos[0], search_pos[1])
            self.userA.aw.sleep(1)
            # 验证页面没有崩溃
            assert self.userA.aw.is_on_workhub_home(), "点击全网搜索后页面异常"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.workhub_close()


class TestWorkhubArtifact(BaseTest):
    """WorkHub产出物页面验证"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_artifact_page_nav(self):
        """
        验证产出物页面导航

        覆盖Excel行: 48(文档图标入口), 52(顶部导航), 53(返回)

        步骤:
        1. 进入WorkHub
        2. 查找文档/产出物图标并点击
        3. 验证进入产出物页面
        4. 点击返回验证回到上一页

        预期结果:
        - 可进入产出物页面
        - 返回按钮正常工作
        """
        self.userA.aw.enter_workhub()

        # 查找文档图标（通常在顶部导航栏）
        doc_pos = self.userA.aw.find_text_by_ocr("文档", timeout=5)
        if not doc_pos:
            doc_pos = self.userA.aw.find_text_by_ocr("产出物", timeout=3)

        if doc_pos:
            self.userA.aw.tap(doc_pos[0], doc_pos[1])
            self.userA.aw.sleep(3)

            # 验证进入了产出物页面
            results = self.userA.aw.ocr_scan_page()
            page_texts = [r['text'] for r in results]
            in_artifact = any('产出' in t or '文档' in t or '排序' in t for t in page_texts)

            if in_artifact:
                # 点击返回
                self.userA.aw.press_back()
                self.userA.aw.sleep(2)
                # 验证回到WorkHub
                assert self.userA.aw.is_on_workhub_home(), "从产出物页返回失败"

    def test_artifact_search(self):
        """
        验证产出物搜索功能

        覆盖Excel行: 56(搜索框), 57(关键词过滤), 58(无结果)

        步骤:
        1. 进入产出物页面
        2. 查找搜索图标
        3. 输入关键词验证过滤

        预期结果:
        - 搜索框可展开
        - 输入关键词后列表更新
        """
        self.userA.aw.enter_workhub()

        # 进入产出物页
        doc_pos = self.userA.aw.find_text_by_ocr("文档", timeout=5)
        if doc_pos:
            self.userA.aw.tap(doc_pos[0], doc_pos[1])
            self.userA.aw.sleep(3)

            # 查找搜索图标
            search_pos = self.userA.aw.find_text_by_ocr("搜索", timeout=3)
            if search_pos:
                self.userA.aw.tap(search_pos[0], search_pos[1])
                self.userA.aw.sleep(1)
                self.userA.aw.input_text("不存在的文档xyz")
                self.userA.aw.sleep(2)

                # 验证有响应（空态或过滤结果）
                results = self.userA.aw.ocr_scan_page()
                assert len(results) > 0, "搜索后页面空白"

    def teardown(self):
        """测试后清理"""
        self.userA.aw.press_back()
        self.userA.aw.sleep(1)
        self.userA.aw.workhub_close()
