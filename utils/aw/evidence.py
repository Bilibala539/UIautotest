"""步骤级证据采集(②证据规范)。

每次操作(点击/滑动/输入)结束后截图,并在截图上标注操作位置:
  - 点击: 红圈 + 十字线标注点击点
  - 滑动: 起终点圆点 + 连线箭头
  - 输入: 文字标注输入内容(无坐标)

通过环境变量 EVIDENCE=1 启用(平台会话自动开启;日常探索/调试不开,
避免拖慢节奏)。证据保存到 output/evidence/<run_tag>/,目录由
EVIDENCE_DIR 或 DASHBOARD_RUN_ID 决定,与平台会话一一对应。
"""
from __future__ import annotations

import logging
import os
from datetime import datetime

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# 标注颜色统一用红色(BGR)
_COLOR = (0, 0, 255)


def _evidence_root() -> str:
    base = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
    run_tag = os.environ.get("EVIDENCE_DIR") or os.environ.get("DASHBOARD_RUN_ID") \
        or datetime.now().strftime("manual_%Y%m%d")
    safe_tag = "".join(c if c not in '\\/:*?"<>|' else "_" for c in run_tag)
    return os.path.join(base, "output", "evidence", safe_tag)


class StepEvidence:
    """会话级步骤证据记录器。disabled 时所有方法是 no-op。"""

    def __init__(self) -> None:
        self.enabled = os.environ.get("EVIDENCE", "").strip() in {"1", "true", "True", "on"}
        self.root = _evidence_root()
        self._counter = 0
        if self.enabled:
            os.makedirs(self.root, exist_ok=True)
            logger.info(f"🖼️ 步骤证据已启用: {self.root}")

    def _next_path(self, op: str) -> str:
        self._counter += 1
        ts = datetime.now().strftime("%H%M%S")
        return os.path.join(self.root, f"{self._counter:03d}_{op}_{ts}.png")

    @staticmethod
    def _annotate_point(img: np.ndarray, point: tuple[int, int]) -> np.ndarray:
        x, y = int(point[0]), int(point[1])
        cv2.circle(img, (x, y), 28, _COLOR, 3)
        cv2.line(img, (x - 40, y), (x + 40, y), _COLOR, 2)
        cv2.line(img, (x, y - 40), (x, y + 40), _COLOR, 2)
        return img

    @staticmethod
    def _annotate_swipe(img: np.ndarray, start: tuple[int, int], end: tuple[int, int]) -> np.ndarray:
        sx, sy = int(start[0]), int(start[1])
        ex, ey = int(end[0]), int(end[1])
        cv2.arrowedLine(img, (sx, sy), (ex, ey), _COLOR, 3, tipLength=0.15)
        cv2.circle(img, (sx, sy), 14, _COLOR, 3)
        cv2.circle(img, (ex, ey), 14, _COLOR, 3)
        return img

    @staticmethod
    def _annotate_label(img: np.ndarray, text: str) -> np.ndarray:
        h, w = img.shape[:2]
        cv2.rectangle(img, (0, h - 56), (w, h), (30, 30, 30), -1)
        cv2.putText(img, text, (12, h - 18), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)
        return img

    def record(self, aw, op: str, point=None, start=None, end=None,
               detail: str = "") -> None:
        """截图并标注当前操作。aw 需提供 take_screenshot()。

        证据只增不阻塞:截图/标注任何失败仅记日志,不向用例抛异常
        (证据缺失不算用例失败,但会在日志中留痕)。
        """
        if not self.enabled:
            return
        try:
            save_path = self._next_path(op)
            img = aw.take_screenshot()  # take_screenshot 自带 HTML 日志内嵌
            if img is None:
                logger.warning(f"⚠️ 证据截图失败({op}),本步骤无截图")
                return
            if point is not None:
                img = self._annotate_point(img, point)
            if start is not None and end is not None:
                img = self._annotate_swipe(img, start, end)
            if detail:
                img = self._annotate_label(img, detail[:60])
            success, buf = cv2.imencode(".png", img)
            if success:
                buf.tofile(save_path)
                logger.info(f"🖼️ 步骤证据[{op}]: {save_path}")
        except Exception as error:  # noqa: BLE001 — 证据失败绝不影响用例
            logger.warning(f"⚠️ 步骤证据采集异常({op}): {error}")


# 模块级单例:AWBase 直接引用
step_evidence = StepEvidence()
