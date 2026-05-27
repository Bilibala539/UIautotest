"""
AW (Action Wrapper) 模块 - 统一入口

基础操作（click_text/find_image/OCR 等）共用一份。
业务方法（login/create_team 等）在 MuMuBusiness 中实现。

使用方式:
    from utils.aw import create_aw

    aw = create_aw(instance_id=0)  # → MuMuBusiness

    aw.login(uid, password)     # 业务方法
    aw.click_text("消息")       # 共用的基础操作
"""

from utils.aw.aw_helper import create_aw, AWHelper
from utils.aw.business.mumu import MuMuBusiness
from utils.aw.driver import MuMuDriver, BasePlatformDriver

__all__ = [
    'create_aw',
    'AWHelper',
    'MuMuBusiness',
    'MuMuDriver',
    'BasePlatformDriver',
]
