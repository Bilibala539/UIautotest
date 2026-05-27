"""
节点用户配置

并行测试时通过 NODE_USERS 环境变量限制每个实例可使用的账号。
"""
import os


def get_node_users() -> list:
    """
    获取当前节点负责的用户列表

    从环境变量 NODE_USERS 读取，如 "userA" 或 "userA,userB"
    未设置时返回 ["userA"]

    Returns:
        list: 用户键名列表
    """
    users_str = os.environ.get("NODE_USERS", "userA")
    return [u.strip() for u in users_str.split(",") if u.strip()]
