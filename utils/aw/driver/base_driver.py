"""
平台驱动抽象基类

定义所有平台驱动必须实现的接口。
AWBase 通过这些接口与底层平台交互，不直接依赖具体平台实现。

接口列表:
  - take_screenshot()       截图，返回 BGR numpy 数组
  - get_window_rect()       获取窗口区域 (left, top, width, height)
  - to_screen_coords(x, y)  窗口内坐标 → 屏幕绝对坐标
  - focus_window()           将目标窗口置于前台
  - tap(x, y)                点击屏幕绝对坐标
  - input_text(text)         输入文字
  - clear_input()            清空输入框
  - press_key(key)           按键
  - swipe(sx, sy, ex, ey)    滑动
  - scroll_up(amount)        向上滚动
  - scroll_down(amount)      向下滚动
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class BasePlatformDriver(ABC):
    """
    平台驱动抽象基类
    
    所有具体平台驱动（MuMuDriver、PCDriver）必须继承此类并实现全部抽象方法。
    """

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """平台标识名称，如 'mumu' 或 'pc'"""
        ...

    # ==================== 窗口操作 ====================

    @abstractmethod
    def get_window_rect(self, refresh: bool = False) -> Optional[Tuple[int, int, int, int]]:
        """
        获取目标窗口客户区在屏幕上的区域

        Args:
            refresh: 是否强制刷新（忽略缓存）

        Returns:
            (left, top, width, height)，失败返回 None
        """
        ...

    @abstractmethod
    def to_screen_coords(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """
        将窗口内相对坐标转换为屏幕绝对坐标

        Args:
            x, y: 窗口内坐标

        Returns:
            (screen_x, screen_y)，失败返回 None
        """
        ...

    @abstractmethod
    def focus_window(self) -> bool:
        """
        将目标窗口置于前台

        Returns:
            bool: 是否成功
        """
        ...

    # ==================== 截图 ====================

    @abstractmethod
    def take_screenshot(self) -> Optional[np.ndarray]:
        """
        截取目标窗口画面

        Returns:
            BGR 格式 numpy 数组，失败返回 None
        """
        ...

    # ==================== 点击 ====================

    @abstractmethod
    def tap(self, screen_x: int, screen_y: int) -> bool:
        """
        点击屏幕绝对坐标

        Args:
            screen_x, screen_y: 屏幕绝对坐标

        Returns:
            bool: 是否成功
        """
        ...

    @abstractmethod
    def long_press(self, screen_x: int, screen_y: int, duration: float = 1.0) -> bool:
        """
        长按屏幕绝对坐标

        Args:
            screen_x, screen_y: 屏幕绝对坐标
            duration: 长按持续时间（秒），默认1.0秒

        Returns:
            bool: 是否成功
        """
        ...

    # ==================== 输入 ====================

    @abstractmethod
    def input_text(self, text: str) -> bool:
        """
        输入文字

        Args:
            text: 要输入的文字

        Returns:
            bool: 是否成功
        """
        ...

    @abstractmethod
    def clear_input(self) -> bool:
        """
        清空当前输入框（全选 + 删除）

        Returns:
            bool: 是否成功
        """
        ...

    # ==================== 按键 ====================

    @abstractmethod
    def press_key(self, key: str) -> bool:
        """
        按下指定按键

        Args:
            key: 按键名称（如 'enter', 'escape', 'tab'）

        Returns:
            bool: 是否成功
        """
        ...

    # ==================== 滑动 / 滚动 ====================

    @abstractmethod
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration: float = 0.3) -> bool:
        """
        从起点滑动到终点（屏幕绝对坐标）

        Args:
            start_x, start_y: 起点屏幕坐标
            end_x, end_y: 终点屏幕坐标
            duration: 滑动耗时（秒）

        Returns:
            bool: 是否成功
        """
        ...

    @abstractmethod
    def scroll(self, screen_x: int, screen_y: int, clicks: int) -> bool:
        """
        在指定位置滚动鼠标滚轮

        Args:
            screen_x, screen_y: 滚动位置的屏幕坐标
            clicks: 正数向上，负数向下

        Returns:
            bool: 是否成功
        """
        ...
