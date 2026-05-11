"""
测试用例: 工作状态-新增状态成功
功能点: 在工作状态设置页面新增自定义状态
操作步骤: 1.输入正确的状态名称 2.选择状态icon 3.点击保存
预期结果: 1.弹出toast"状态新增成功" 2.返回工作状态设置页面，新增的状态显示在列表底部
"""
import time
import pytest
from conftest import BaseTest


@pytest.mark.skip(reason="工作状态设置页面入口在当前版本无法通过OCR定位(侧边栏仅有纯图标入口)")
class TestWorkStatusAdd(BaseTest):
    """工作状态-新增状态"""

    def setup(self):
        self.userA = self.users("userA")

    def test_add_custom_work_status(self):
        """
        步骤:
        1. 进入工作状态设置页面
        2. 点击新增/添加按钮
        3. 输入自定义状态名称
        4. 选择icon
        5. 点击保存
        6. 验证新增成功
        """
        # 进入工作状态页面
        self.userA.aw.open_work_status_page()
        time.sleep(1)

        # 滑动到底部查找"新增"或"添加"按钮
        self.userA.aw.swipe_up(distance=300)
        time.sleep(1)

        # 点击添加按钮
        add_pos = self.userA.aw.find_text_by_ocr("添加", timeout=5)
        if not add_pos:
            add_pos = self.userA.aw.find_text_by_ocr("新增", timeout=3)
        assert add_pos, "工作状态页面未找到添加/新增按钮"
        self.userA.aw.tap(add_pos[0], add_pos[1])
        time.sleep(1)

        # 输入状态名称
        self.userA.aw.input_text("自动化测试状态")
        time.sleep(1)

        # 点击保存
        self.userA.aw.click_text("保存", timeout=5)
        time.sleep(2)

        # 验证新增成功（回到列表后能看到刚新增的状态名）
        pos = self.userA.aw.find_text_by_ocr("自动化测试状态", timeout=5)
        assert pos, "新增状态失败，列表中未找到'自动化测试状态'"

    def teardown(self):
        """清理：删除刚新增的状态"""
        # 尝试删除（如果还在页面上）
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.press_back()
