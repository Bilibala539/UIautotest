"""Android 端基础操作（AndroidBaseAW）。

按键、返回、Home 等 Android 系统级操作收敛在这里。
"""
from __future__ import annotations

import logging

from utils.aw.aw_base import AWBase, _screenshot_on_failure

logger = logging.getLogger(__name__)


class AndroidBaseAW(AWBase):
    """android 端基础操作，继承公共引擎 AWBase。"""

    # ==================== 系统按键 ====================

    def press_key(self, key: str) -> bool:
        """按下系统按键（如 'escape'、'home'）。"""
        result = self.driver.press_key(key)
        self.sleep(0.2)
        return result

    def press_back(self) -> bool:
        """按返回键。"""
        logger.info("🔙 按返回键")
        return self.press_key('escape')

    def press_home(self) -> bool:
        """按 Home 键。"""
        return self.press_key('home')
