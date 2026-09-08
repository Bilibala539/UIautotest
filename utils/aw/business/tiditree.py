"""TidiTree 项目业务方法（web 端）。

TidiTree 目前只有 web 端；项目专属业务方法放这里。
"""
from __future__ import annotations

from utils.aw.base.web_base import WebBaseAW
from utils.aw.business.common import CommonBusinessMixin


class TidiTreeBusiness(CommonBusinessMixin, WebBaseAW):
    """TidiTree 项目业务编排（web 端），TidiTree 专属方法放这里。"""
