"""
分布式测试节点配置

支持多台PC协同执行PC端POPO测试：
- 每台机器独立运行pytest，操作本地的POPO窗口
- 通过协调服务(Coordinator)同步多用户的操作时序
- 零延迟：每台机器都是本地操作，不需要SSH远程执行

架构:
  开发机 (NODE=local, USERS=userA)          笔记本 (NODE=remote1, USERS=userB)
  ┌──────────────────────┐                  ┌──────────────────────┐
  │ pytest               │                  │ pytest               │
  │ userA = PPUser(pc)   │                  │ userB = PPUser(pc)   │
  │ PCDriver → 本地POPO  │                  │ PCDriver → 本地POPO  │
  │       ↑              │                  │       ↑              │
  │    零延迟             │                  │    零延迟             │
  └──────┬───────────────┘                  └──────┬───────────────┘
         │                                         │
         │         Coordinator (服务器)              │
         │  ┌──────────────────────────┐           │
         └──►  HTTP API :9877         ◄───────────┘
            │  /sync  - 操作同步       │
            │  /wait   - 等待对端操作   │
            │  /notify - 通知对端完成   │
            └──────────────────────────┘

使用方式:
  # 开发机 (userA)
  set NODE=local
  set NODE_USERS=userA
  set COORDINATOR_URL=http://服务器IP:9877
  pytest tests/win/ -v

  # 笔记本 (userB)
  set NODE=remote1
  set NODE_USERS=userB
  set COORDINATOR_URL=http://服务器IP:9877
  pytest tests/win/ -v

  # 服务器 (协调器)
  python tools/coordinator_server.py --port 9877
"""
import logging
import os
import time
import json
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class CoordinatorClient:
    """
    协调器客户端

    用于多节点之间的操作同步。当 userA 需要等待 userB 完成某个操作时，
    通过协调器进行同步。

    使用示例:
        # userA 发送消息后，等待 userB 确认收到
        coordinator = CoordinatorClient("http://服务器:9877", node="local")
        coordinator.notify("message_sent", data={"from": "userA", "text": "Hello"})
        coordinator.wait_for("message_received", timeout=30)

        # userB 等待 userA 发送消息
        coordinator.wait_for("message_sent", timeout=30)
        # userB 确认收到
        coordinator.notify("message_received", data={"by": "userB"})
    """

    def __init__(self, url: str, node: str):
        """
        Args:
            url: 协调器服务地址 (如 http://192.168.1.50:9877)
            node: 当前节点名称 (如 local, remote1)
        """
        self.url = url.rstrip('/')
        self.node = node
        self._session = requests.Session()

    def notify(self, event: str, data: dict = None) -> bool:
        """
        通知协调器某个事件已发生

        Args:
            event: 事件名称
            data: 事件数据

        Returns:
            bool: 是否成功
        """
        try:
            resp = self._session.post(
                f"{self.url}/notify",
                json={"node": self.node, "event": event, "data": data or {}},
                timeout=5,
            )
            if resp.status_code == 200:
                logger.info(f"📢 [协调] 通知事件: {event}")
                return True
            logger.error(f"❌ [协调] 通知失败: HTTP {resp.status_code}")
            return False
        except Exception as e:
            logger.error(f"❌ [协调] 通知失败: {e}")
            return False

    def wait_for(self, event: str, timeout: int = 60, poll_interval: float = 1.0) -> Optional[dict]:
        """
        等待某个事件发生

        Args:
            event: 等待的事件名称
            timeout: 超时时间(秒)
            poll_interval: 轮询间隔(秒)

        Returns:
            dict: 事件数据，超时返回 None
        """
        logger.info(f"⏳ [协调] 等待事件: {event} (超时={timeout}s)")
        start = time.time()
        while time.time() - start < timeout:
            try:
                resp = self._session.get(
                    f"{self.url}/wait",
                    params={"event": event, "node": self.node, "timeout": min(poll_interval * 2, 5)},
                    timeout=poll_interval * 2 + 2,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("ready"):
                        logger.info(f"✅ [协调] 事件已到达: {event}")
                        return result.get("data", {})
            except requests.exceptions.Timeout:
                pass
            except Exception as e:
                logger.debug(f"[协调] 轮询异常: {e}")
            time.sleep(poll_interval)

        logger.error(f"❌ [协调] 等待超时: {event} ({timeout}s)")
        return None

    def barrier(self, name: str, count: int = 2, timeout: int = 120) -> bool:
        """
        屏障同步 - 等待所有节点都到达此点

        Args:
            name: 屏障名称
            count: 需要同步的节点数
            timeout: 超时时间(秒)

        Returns:
            bool: 是否所有节点都已到达
        """
        logger.info(f"🚧 [协调] 屏障同步: {name} (需要{count}个节点)")
        try:
            resp = self._session.post(
                f"{self.url}/barrier",
                json={"name": name, "node": self.node, "count": count},
                timeout=timeout + 5,
            )
            if resp.status_code == 200:
                result = resp.json()
                if result.get("ready"):
                    logger.info(f"✅ [协调] 屏障通过: {name}")
                    return True
            logger.error(f"❌ [协调] 屏障超时: {name}")
            return False
        except Exception as e:
            logger.error(f"❌ [协调] 屏障失败: {e}")
            return False

    def reset(self) -> bool:
        """重置协调器状态（测试开始前调用）"""
        try:
            resp = self._session.post(f"{self.url}/reset", timeout=5)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"❌ [协调] 重置失败: {e}")
            return False


def get_coordinator() -> Optional[CoordinatorClient]:
    """
    获取协调器客户端实例

    从环境变量读取配置:
    - COORDINATOR_URL: 协调器地址
    - NODE: 当前节点名称

    Returns:
        CoordinatorClient 或 None（未配置时返回None）
    """
    url = os.environ.get("COORDINATOR_URL")
    node = os.environ.get("NODE", "local")
    if url:
        return CoordinatorClient(url, node)
    return None


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


def get_node_name() -> str:
    """
    获取当前节点名称

    Returns:
        str: 节点名称
    """
    return os.environ.get("NODE", "local")
