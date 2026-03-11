"""
中级AW方法 - 已合并到aw_base.py

此文件保留用于向后兼容，所有功能已合并到AWBase类中
"""
from utils.aw.aw_base import AWBase

# 为了向后兼容，AWAction现在是AWBase的别名
AWAction = AWBase