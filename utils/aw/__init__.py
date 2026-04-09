"""
AW (Action Wrapper) 模块 - 统一入口

基础操作（click_text/find_image/OCR 等）共用一份。
业务方法（login/create_team 等）按平台分离。

使用方式:
    from utils.aw import create_aw

    aw = create_aw(platform="mumu", instance_id=0)  # → MuMuBusiness
    aw = create_aw(platform="pc")                    # → PCBusiness

    aw.login(uid, password)     # 各自的实现
    aw.click_text("消息")       # 共用的基础操作
"""

from utils.aw.aw_helper import create_aw, AWHelper
from utils.aw.business.mumu import MuMuBusiness
from utils.aw.business.pc import PCBusiness
from utils.aw.driver import MuMuDriver, PCDriver, BasePlatformDriver

__all__ = [
    'create_aw',
    'AWHelper',
    'MuMuBusiness',
    'PCBusiness',
    'MuMuDriver',
    'PCDriver',
    'BasePlatformDriver',
]