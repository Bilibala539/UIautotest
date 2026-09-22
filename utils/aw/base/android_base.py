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

    # ==================== 首启弹窗自动处置 ====================

    # (界面标志文字含匹配, 按钮/动作文字精确匹配);新弹窗=追加一条规则
    APP_POPUP_RULES: tuple[tuple[str, str], ...] = (
        ("用户隐私协议概要", "同意"),      # App 首启隐私协议
        ("欢迎使用Swan Audio", "稍后再说"),  # 平台授权弹窗(授权需先勾选置灰,只点稍后再说)
        ("是否允许", "允许"),              # Android 系统权限弹窗
    )

    def dismiss_app_popups(self, rules: tuple[tuple[str, str], ...] = APP_POPUP_RULES,
                           rounds: int = 3) -> list[str]:
        """打开 App 后自动检测并处置首启/系统弹窗(用户拍板的框架级检测)。

        标志文字出现才动作,按钮按文字精确匹配(经语义节点定位,不写坐标);
        白名单外的弹窗不动,只记 WARNING 供人工补规则。返回处置记录。
        """
        handled: list[str] = []
        for _ in range(rounds):
            nodes = self.driver.dump_nodes()
            hit = None
            for marker, button in rules:
                if not any(marker in (n["text"] or "") or marker in (n["content_desc"] or "")
                           for n in nodes):
                    continue
                target = next((n for n in nodes
                               if button in (n["text"], n["content_desc"]) and n["center"]), None)
                if target is None:
                    logger.warning(f"弹窗 '{marker}' 出现但未找到按钮 '{button}',跳过(需补规则)")
                    continue
                hit = (marker, button, target)
                break
            if hit is None:
                return handled
            marker, button, target = hit
            logger.info(f"自动处置弹窗 '{marker}' → 点击 '{button}'")
            self.tap(*target["center"])
            handled.append(marker)
            self.sleep(1.5)  # 关闭动画后可能还有下一层弹窗
        logger.warning(f"弹窗处置 {rounds} 轮未清空,已处置: {handled}(界面可能仍有弹窗)")
        return handled
