"""
统一 AW Helper - 用户调用入口

根据 platform 参数自动选择:
  - 底层驱动 (MuMuDriver / PCDriver)
  - 业务实现 (MuMuBusiness / PCBusiness)

使用方式:
    aw = AWHelper(platform="mumu", instance_id=0)
    aw.login(uid, password)      # → MuMuBusiness.login()
    aw.click_text("消息")        # → AWBase.click_text() (共用)

    aw = AWHelper(platform="pc")
    aw.login(uid, password)      # → PCBusiness.login()
    aw.click_text("消息")        # → AWBase.click_text() (共用)
"""
import logging
from typing import Optional, List, Union

from utils.aw.business.mumu import MuMuBusiness
from utils.aw.business.pc import PCBusiness
from utils.aw.driver.base_driver import BasePlatformDriver
from utils.aw.driver.mumu_driver import MuMuDriver
from utils.aw.driver.pc_driver import PCDriver

logger = logging.getLogger(__name__)

# AWHelper 的类型: MuMuBusiness 或 PCBusiness
AWHelper = Union[MuMuBusiness, PCBusiness]


def create_aw(platform: str, instance_id: int = 0,
              window_keywords: Optional[List[str]] = None) -> AWHelper:
    """
    创建 AW 实例

    根据 platform 参数自动选择对应的驱动和业务类。

    Args:
        platform: 'mumu' 或 'pc'
        instance_id: MuMu 模拟器实例ID (仅 mumu 使用)
        window_keywords: PC 端窗口标题关键词 (仅 pc 使用)

    Returns:
        MuMuBusiness 或 PCBusiness 实例
    """
    if platform == "mumu":
        driver = MuMuDriver(instance_id=instance_id)
        return MuMuBusiness(driver)
    elif platform == "pc":
        driver = PCDriver(window_keywords=window_keywords)
        return PCBusiness(driver)
    else:
        raise ValueError(f"❌ 不支持的平台: '{platform}'，可选: 'mumu', 'pc'")
