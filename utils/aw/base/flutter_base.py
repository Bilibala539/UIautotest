"""Flutter 端基础操作（FlutterBaseAW）。

accessibility（语义树）定位操作收敛在这里；flutter 端新增基础操作放这里。
"""
from __future__ import annotations

import logging
import time
from typing import Optional

import cv2
import numpy as np

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

    # ==================== toast 捕获 ====================

    def wait_toast(self, text: str, timeout: float = 4.0,
                   region=None) -> bool:
        """等待并捕获 toast 文本（OCR），出现返回 True（由调用方断言）。

        Android toast 会渲染进截屏但约 2~3.5s 即消失，本方法必须在触发动作后
        **立即**调用；内部为 OCR 轮询（find_text_by_ocr），region 传 toast
        常驻的屏幕下部区域可提高捕获率并加快单帧速度。
        """
        found = self.find_text_by_ocr(text, timeout=int(timeout), region=region)
        return found is not None

    # ==================== 系统按键（扩展） ====================

    def long_press_key(self, key: str) -> bool:
        """长按系统按键（如音量键），走 driver 的 keyevent --longpress。"""
        return self.press_key(key, long_press=True)

    # ==================== 动态区域检测 ====================

    def region_changed(self, x: int, y: int, w: int, h: int,
                       gap: float = 0.5, samples: int = 3,
                       threshold: float = 2.0) -> bool:
        """检测屏幕区域内画面是否在动（黑胶唱片旋转、歌词滚动等）。

        连续截 samples 帧（相邻帧间隔 gap 秒），区域灰度图的平均绝对差
        超过 threshold（0~255）即判定在动。注意 adb 截屏本身有耗时，
        帧间隔实际不小于 gap；threshold 默认 2.0，静态 UI 噪声通常 <1。
        """
        region_img: Optional[np.ndarray] = None
        for i in range(samples):
            img = self.take_screenshot()
            if img is not None:
                crop = img[y:y + h, x:x + w]
                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                if region_img is not None:
                    diff = float(cv2.absdiff(gray, region_img).mean())
                    if diff > threshold:
                        logger.info(f"🎬 区域({x},{y},{w},{h})在动: 平均差 {diff:.2f}")
                        return True
                region_img = gray
            if i < samples - 1:
                self.sleep(gap)
        logger.info(f"🎬 区域({x},{y},{w},{h})静止")
        return False

    # ==================== 元素锚定滑动 ====================

    @_screenshot_on_failure
    def drag_on_template(self, template: str, start_ratio: float, end_ratio: float,
                         axis: str = "x", threshold: float = 0.8, timeout: int = 10,
                         region=None, duration: float = 0.5) -> bool:
        """以模板图片矩形为锚做比例滑动（滑条/进度条）。元素锚定手势，非坐标回退。

        find_image_rect 定位整条控件矩形，沿 axis 在矩形上按比例取起止点后 swipe。

        Args:
            start_ratio/end_ratio: 0~1，沿滑动轴在控件矩形内的相对位置
            axis: "x" 横向滑条（进度条）/ "y" 纵向滑条（音量条）
        """
        assert axis in ("x", "y"), "axis 仅支持 x / y"
        rect = self.find_image_rect(template, threshold=threshold, timeout=timeout,
                                    region=region)
        assert rect is not None, f"元素锚定滑动失败: 未找到 '{template}'"
        rx, ry, rw, rh = rect
        if axis == "x":
            start = (rx + int(rw * start_ratio), ry + rh // 2)
            end = (rx + int(rw * end_ratio), ry + rh // 2)
        else:
            start = (rx + rw // 2, ry + int(rh * start_ratio))
            end = (rx + rw // 2, ry + int(rh * end_ratio))
        logger.info(f"🎚️ 元素锚定滑动 '{template}' {start_ratio:.2f}→{end_ratio:.2f} "
                    f"{start}→{end}")
        return self.swipe(start[0], start[1], end[0], end[1], duration)
