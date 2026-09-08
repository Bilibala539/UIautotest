"""安卓项目业务方法（android 端）。

注意：该项目为独立的智能音箱显示屏系统，正式项目名确定后
将 AndroidBusiness / 本文件全局重命名为 <项目名>Business / <项目名>.py。
"""
from __future__ import annotations

import os

from utils.aw.base.android_base import AndroidBaseAW
from utils.aw.business.common import CommonBusinessMixin


class AndroidBusiness(CommonBusinessMixin, AndroidBaseAW):
    """安卓项目（智能音箱屏系统，名称待定）业务编排。"""

    def start_app(self, package: str = "") -> None:
        """通过 adb 启动 App 并等待冷启动完成。"""
        package = package or os.environ.get("SWAN_PACKAGE", "com.swan.network").strip()
        starter = getattr(self.driver, "start_app", None)
        if starter is None:
            raise RuntimeError(f"当前驱动不支持 start_app: {type(self.driver).__name__}")
        starter(package)
        self.sleep(1)
