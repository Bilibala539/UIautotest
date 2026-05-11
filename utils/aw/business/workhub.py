"""
WorkHub (AI首页) 业务方法

包含 WorkHub WebView 内的业务操作流程。
通过 POPO 搜索页"问AI"Tab 进入 WorkHub。
"""
import logging
import time
from typing import Optional, Tuple, List

from utils.aw.business.common import CommonBusiness
from utils.aw.driver.base_driver import BasePlatformDriver
from utils.aw.search_region import Normal

logger = logging.getLogger(__name__)


class WorkHubBusiness(CommonBusiness):
    """
    WorkHub 业务类

    继承链: WorkHubBusiness → CommonBusiness → AWBase
    提供 WorkHub WebView 内的所有业务操作方法。
    """

    # ==================== 导航方法 ====================

    def enter_workhub(self) -> bool:
        """
        从POPO消息列表页进入WorkHub

        步骤:
        1. 点击搜索按钮
        2. 点击"问AI"Tab
        3. 等待WorkHub页面加载
        4. 验证WorkHub标题出现

        Returns:
            bool: 是否成功进入WorkHub
        """
        logger.info("🚀 进入WorkHub...")

        # 点击搜索按钮(右上角)
        self.tap(432, 72)
        self.sleep(1)

        # 点击"问AI"Tab
        self.click_text("问AI", timeout=5)
        self.sleep(3)

        # 处理可能的引导弹窗
        guide_pos = self.find_text_by_ocr("我知道了", timeout=3)
        if guide_pos:
            self.tap(guide_pos[0], guide_pos[1])
            self.sleep(1)

        # 验证是否进入了WorkHub
        workhub_pos = self.find_text_by_ocr("WorkHub", timeout=10)
        if workhub_pos:
            logger.info("✅ 成功进入WorkHub")
            return True

        logger.error("❌ 未能进入WorkHub")
        return False

    def is_on_workhub_home(self) -> bool:
        """
        检查当前是否在WorkHub首页

        Returns:
            bool: 是否在WorkHub首页
        """
        pos = self.find_text_by_ocr("WorkHub", timeout=3)
        return pos is not None

    def get_visible_skill_tabs(self) -> List[str]:
        """
        获取当前可见的技能Tab列表

        Returns:
            List[str]: 可见的Tab名称列表
        """
        results = self.ocr_scan_page(region=(0, 330, 540, 60))
        return [r['text'] for r in results]

    def get_model_name(self) -> Optional[str]:
        """
        获取当前显示的模型名称

        Returns:
            Optional[str]: 模型名称，如 "Kimi K2.6"
        """
        results = self.ocr_scan_page(region=(0, 860, 300, 60))
        for r in results:
            if 'Kimi' in r['text'] or 'Claude' in r['text'] or 'DeepSeek' in r['text'] or 'Gemini' in r['text']:
                return r['text']
        return None

    def click_model_name(self) -> bool:
        """
        点击模型名称打开模型切换浮层

        Returns:
            bool: 是否成功点击
        """
        model = self.get_model_name()
        if model:
            pos = self.find_text_by_ocr(model, timeout=3, region=(0, 860, 300, 60))
            if pos:
                self.tap(pos[0], pos[1])
                self.sleep(1)
                return True
        return False

    def open_sidebar(self) -> bool:
        """
        点击左上角汉堡按钮打开侧边栏

        Returns:
            bool: 是否成功打开侧边栏
        """
        logger.info("📱 打开WorkHub侧边栏...")
        # 汉堡按钮在左上角
        self.tap(40, 82)
        self.sleep(2)

        # 验证侧边栏打开（应该能看到"订阅"或"历史记录"）
        subscribe_pos = self.find_text_by_ocr("订阅", timeout=3)
        history_pos = self.find_text_by_ocr("历史记录", timeout=2)
        if subscribe_pos or history_pos:
            logger.info("✅ 侧边栏已打开")
            return True

        logger.error("❌ 侧边栏未打开")
        return False

    def close_workhub(self) -> bool:
        """
        点击右上角X关闭WorkHub返回消息列表

        Returns:
            bool: 是否成功关闭
        """
        logger.info("❌ 关闭WorkHub...")
        self.tap(500, 82)
        self.sleep(2)
        return True

    # ==================== 侧边栏操作 ====================

    def sidebar_click_subscribe(self) -> bool:
        """
        在侧边栏中点击"订阅"入口

        Returns:
            bool: 是否成功进入订阅页
        """
        self.click_text("订阅", timeout=5)
        self.sleep(3)
        # 验证进入订阅页
        title_pos = self.find_text_by_ocr("订阅", timeout=5, region=(0, 40, 540, 60))
        return title_pos is not None

    def sidebar_click_new_dialog(self) -> bool:
        """
        在侧边栏中点击"+新对话"

        Returns:
            bool: 是否成功创建新对话
        """
        new_pos = self.find_text_by_ocr("新对话", timeout=3)
        if new_pos:
            self.tap(new_pos[0], new_pos[1])
            self.sleep(2)
            return True
        return False

    # ==================== 输入与发送 ====================

    def click_input_box(self) -> bool:
        """
        点击底部输入框使其聚焦

        Returns:
            bool: 是否成功聚焦
        """
        input_pos = self.find_text_by_ocr("分配任务或提问", timeout=5)
        if input_pos:
            self.tap(input_pos[0], input_pos[1])
            self.sleep(1)
            return True
        # 备选：直接点击输入框区域
        self.tap(207, 818)
        self.sleep(1)
        return True

    def input_slash(self) -> bool:
        """
        在输入框中输入"/"触发技能选择浮层

        Returns:
            bool: 是否成功触发浮层
        """
        self.click_input_box()
        self.sleep(0.5)
        self.input_text("/")
        self.sleep(2)
        return True

    # ==================== 技能Tab切换 ====================

    def click_skill_tab(self, tab_name: str) -> bool:
        """
        点击技能Tab区的某个Tab

        Args:
            tab_name: Tab名称，如"通用"、"创建多维表格"等

        Returns:
            bool: 是否成功点击
        """
        pos = self.find_text_by_ocr(tab_name, timeout=5, region=(0, 330, 540, 60))
        if pos:
            self.tap(pos[0], pos[1])
            self.sleep(2)
            return True
        return False
