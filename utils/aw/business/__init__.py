"""业务 AW 层统一入口：按项目分，每项目一套业务类。

维度模型：
- 基础 AW 按端分 → utils/aw/base/（WebBaseAW / AndroidBaseAW / FlutterBaseAW）
- 业务 AW 按项目分 → 本包（TidiTreeBusiness / AndroidBusiness / SwanBusiness）
- 一个端可以挂多个项目，新项目只需新增 <项目>.py + <项目>User

组合方式::

    class SwanBusiness(CommonBusinessMixin, FlutterBaseAW): ...

用法::

    biz = create_business(driver)      # 按平台自动选择业务类
    biz.login_by_sms("13777777777")    # 业务方法，内部调用端 base 基础操作
"""
from __future__ import annotations

from utils.aw.business.common import CommonBusinessMixin
from utils.aw.business.tiditree import TidiTreeBusiness
from utils.aw.business.android import AndroidBusiness
from utils.aw.business.swan import SwanBusiness

__all__ = [
    "CommonBusinessMixin",
    "TidiTreeBusiness",
    "AndroidBusiness",
    "SwanBusiness",
    "create_business",
]

_BUSINESS_BY_PLATFORM = {
    "web": TidiTreeBusiness,
    "android": AndroidBusiness,
    "flutter": SwanBusiness,
}


def create_business(driver):
    """根据驱动的 ``platform_name`` 创建对应的业务层实例。

    Args:
        driver: :class:`BasePlatformDriver` 实例（含 ``platform_name``）。

    Raises:
        ValueError: 平台没有对应的业务类。
    """
    platform = getattr(driver, "platform_name", "")
    business_cls = _BUSINESS_BY_PLATFORM.get(platform)
    if business_cls is None:
        raise ValueError(f"未知平台，无法创建业务层: {platform!r}")
    return business_cls(driver)
