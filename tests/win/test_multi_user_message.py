"""
测试用例: PC端多用户消息交互测试（分布式版本）

本用例需要在两台PC上同时运行，每台机器只操作自己负责的用户。

运行方式:
  # 服务器上启动协调器
  python tools/coordinator_server.py --port 9877

  # 开发机 (userA)
  set PLATFORM=pc
  set NODE=local
  set NODE_USERS=userA
  set COORDINATOR_URL=http://服务器IP:9877
  pytest tests/win/test_multi_user_message.py -v

  # 笔记本 (userB)
  set PLATFORM=pc
  set NODE=remote1
  set NODE_USERS=userB
  set COORDINATOR_URL=http://服务器IP:9877
  pytest tests/win/test_multi_user_message.py -v

前置条件:
  1. 服务器上运行: python tools/coordinator_server.py --port 9877
  2. 两台机器上都运行 POPO PC 客户端（各自登录自己的账号）
  3. 两台机器上都部署了本项目
"""
from conftest import BaseTest
from utils.distributed import get_coordinator, get_node_users


class TestMultiUserMessage(BaseTest):
    """PC端多用户消息交互测试类（分布式）"""

    def setup(self):
        """
        测试前初始化
        - 根据 NODE_USERS 环境变量，只实例化当前节点负责的用户
        - NODE_USERS=userA → 只创建 userA
        - NODE_USERS=userB → 只创建 userB
        """
        self.coordinator = get_coordinator()
        self.my_users = get_node_users()

        # 只创建当前节点负责的用户
        if "userA" in self.my_users:
            self.userA = self.users("userA")
        if "userB" in self.my_users:
            self.userB = self.users("userB")

    def test_send_and_receive_message(self):
        """
        测试场景: userA 发送消息，userB 接收消息

        分布式执行流程:
        ┌─────────────────────┐    ┌─────────────────────┐
        │ 开发机 (userA)       │    │ 笔记本 (userB)       │
        │                     │    │                     │
        │ barrier("start") ───┼───►│ barrier("start")    │
        │ send_message()      │    │                     │
        │ notify("sent") ─────┼───►│ wait_for("sent")    │
        │                     │    │ text_exists()        │
        │ wait_for("received")◄────┤ notify("received")  │
        └─────────────────────┘    └─────────────────────┘
        """
        # Step 1: 屏障同步 - 确保两端都准备好了
        if self.coordinator:
            self.coordinator.barrier("test_start", count=2, timeout=60)

        # Step 2-3: userA 发送消息并通知
        if "userA" in self.my_users:
            self.userA.send_message("grp.popoqa93", "分布式测试消息")
            if self.coordinator:
                self.coordinator.notify("message_sent", data={"text": "分布式测试消息"})

        # Step 4-5: userB 等待消息并验证
        if "userB" in self.my_users:
            if self.coordinator:
                self.coordinator.wait_for("message_sent", timeout=30)
            self.userB.text_exists("分布式测试消息")
            if self.coordinator:
                self.coordinator.notify("message_received", data={"by": "userB"})

        # Step 6: userA 等待 userB 确认
        if "userA" in self.my_users:
            if self.coordinator:
                self.coordinator.wait_for("message_received", timeout=30)

    def teardown(self):
        """测试后清理"""
        pass
