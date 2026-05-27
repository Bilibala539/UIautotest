"""
统一 AW Helper - 用户调用入口

使用方式:
    aw = create_aw(instance_id=0)
    aw.login(uid, password)      # → MuMuBusiness.login()
    aw.click_text("消息")        # → AWBase.click_text() (共用)
"""
import logging

from utils.aw.business.mumu import MuMuBusiness
from utils.aw.driver.mumu_driver import MuMuDriver

logger = logging.getLogger(__name__)

AWHelper = MuMuBusiness


def create_aw(instance_id: int = 0) -> MuMuBusiness:
    """
    创建 AW 实例

    Args:
        instance_id: MuMu 模拟器实例ID

    Returns:
        MuMuBusiness 实例
    """
    driver = MuMuDriver(instance_id=instance_id)
    return MuMuBusiness(driver)
