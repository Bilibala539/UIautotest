"""
平台驱动模块

提供 MuMu (Android) 和 PC (Windows) 两种平台驱动，
由统一的 AWBase 通过 driver 接口调用，实现一套 AW 方法兼容双端。
"""

from utils.aw.driver.base_driver import BasePlatformDriver
from utils.aw.driver.mumu_driver import MuMuDriver
from utils.aw.driver.pc_driver import PCDriver

__all__ = [
    'BasePlatformDriver',
    'MuMuDriver',
    'PCDriver',
]
