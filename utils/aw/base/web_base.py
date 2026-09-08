"""Web 端基础操作（WebBaseAW）。

TidiTree 等 web 项目的公共操作入口；web 端新增基础操作放这里。
"""
from __future__ import annotations

from utils.aw.aw_base import AWBase


class WebBaseAW(AWBase):
    """web 端基础操作，继承公共引擎 AWBase。"""

    # TODO: web 端专属操作（如元素选择器点击、frame 切换）后续收敛到这里
