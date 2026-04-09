"""
业务层模块

按平台分离的业务方法实现:
  - common.py : 两端通用的业务方法
  - mumu.py   : MuMu (Android) 端专属业务方法
  - pc.py     : PC (Windows) 端专属业务方法
"""
from utils.aw.business.mumu import MuMuBusiness
from utils.aw.business.pc import PCBusiness

__all__ = ['MuMuBusiness', 'PCBusiness']
