"""Flutter 端基础操作（FlutterBaseAW）。

accessibility（语义树）定位操作收敛在这里；flutter 端新增基础操作放这里。
"""
from __future__ import annotations

import logging
import time

from utils.aw.aw_base import _screenshot_on_failure
from utils.aw.base.android_base import AndroidBaseAW

logger = logging.getLogger(__name__)


class FlutterBaseAW(AndroidBaseAW):
    """flutter 端基础操作，继承 AndroidBaseAW（flutter 跑在 Android 设备上）。"""

    # ==================== accessibility 定位 ====================

    def accessibility_exists(self, resource_id: str) -> bool:
        """判断 accessibility 节点是否存在。"""
        return self.driver.accessibility_exists(resource_id)

    @_screenshot_on_failure
    def click_accessibility(self, resource_id: str) -> bool:
        """通过平台语义节点定位并点击，不在用例中固化坐标。"""
        finder = getattr(self.driver, "find_node_center", None)
        if finder is None:
            raise RuntimeError(f"当前平台驱动不支持语义节点定位: {resource_id}")
        position = finder(resource_id)
        assert position is not None, f"未找到语义节点 '{resource_id}'"
        return self.tap(position[0], position[1])

    def wait_accessibility(self, resource_id: str, timeout: float = 10.0,
                           interval: float = 0.5) -> bool:
        """轮询等待语义节点出现，超时返回 False（不抛异常，由调用方断言）。"""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.accessibility_exists(resource_id):
                logger.info(f"✅ 语义节点 '{resource_id}' 已出现")
                return True
            time.sleep(interval)
        logger.error(f"❌ 等待语义节点 '{resource_id}' 超时（{timeout}s）")
        return False

    # ==================== 语义树 dump（探索用） ====================

    def dump_semantics(self) -> list[dict]:
        """dump 当前页面语义节点列表（resource_id/text/content_desc/bounds 等）。

        这是 accessibility key 的唯一合法来源，仅供 explorer 探索与调试，
        业务方法禁止依赖 dump 做定位（定位一律走 click_accessibility）。
        """
        nodes = self.driver.dump_nodes()
        logger.info(f"semantic dump: {len(nodes)} 个节点")
        return nodes

    def print_semantics(self, clickable_only: bool = False) -> None:
        """把语义树 dump 成可读表格打印到日志/控制台。"""
        nodes = self.dump_semantics()
        if clickable_only:
            nodes = [n for n in nodes if n["clickable"]]
        print(f"{'click':<5} {'resource_id':<45} {'text/desc':<30} bounds")
        print("-" * 110)
        for n in nodes:
            label = n["text"] or n["content_desc"]
            box = n["bounds"]
            bounds_str = f"[{box[0]},{box[1]}][{box[2]},{box[3]}]" if box else "?"
            print(f"{'*' if n['clickable'] else '':<5} "
                  f"{n['resource_id']:<45} {label:<30} {bounds_str}")
