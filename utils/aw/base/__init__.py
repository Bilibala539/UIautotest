"""基础 AW 层：按端划分的操作方法，每端一套。

- WebBaseAW     ← web 端操作（选择器点击等）
- AndroidBaseAW ← android 端操作（press_back / press_home …）
- FlutterBaseAW ← flutter 端操作（accessibility 系列），继承 AndroidBaseAW

公共引擎（OCR/截图/图像匹配）在 ``aw_base.AWBase``，各端 base 继承它。
新增端专属操作时放对应端的 base，不要放回 AWBase。
"""
from utils.aw.aw_base import AWBase
from utils.aw.base.web_base import WebBaseAW
from utils.aw.base.android_base import AndroidBaseAW
from utils.aw.base.flutter_base import FlutterBaseAW

__all__ = ["AWBase", "WebBaseAW", "AndroidBaseAW", "FlutterBaseAW"]
