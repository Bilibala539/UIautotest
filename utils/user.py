"""测试用户入口：按项目区分 TTUser（TidiTree）、AndroidUser（智能音箱屏）与 SwanUser（Swan）。

用户类 = 项目 × 端 的组合入口：
- TTUser    → TidiTreeBusiness（web 端）
- AndroidUser → AndroidBusiness（android 端，项目名待定）
- SwanUser  → SwanBusiness（flutter 端）

业务方法经 ``__getattr__`` 自动代理到 ``self.business``，因此
``userA.login_by_sms()``、``userA.playmusic()`` 无需在用户类中逐一定义；
基础操作同理（业务类继承了端 base），``user.aw`` 直接就是业务实例。
"""
from __future__ import annotations

from typing import Optional, Type

from utils.aw.business import AndroidBusiness, SwanBusiness, TidiTreeBusiness
from utils.aw.driver.base_driver import BasePlatformDriver
from utils.aw.driver.web_driver import SeleniumWebDriver


class User:
    """通用测试用户：关联一个平台会话 + 业务层（内含端 base 全部操作）。

    传入 ``browser`` 时使用 Selenium WebDriver；传入 ``driver`` 时直接
    使用给定的平台驱动。业务层实例即 ``user.aw``，同时具备
    端基础操作（click_text/input_text/…）与项目业务方法（login_by_sms/…）。

    子类通过 ``business_cls`` 固定业务层类型。
    """

    business_cls: Optional[Type] = None

    def __init__(
        self,
        browser=None,
        username: str = "",
        password: str = "",
        name: str = "",
        driver: Optional[BasePlatformDriver] = None,
    ):
        if browser is not None and driver is not None:
            raise ValueError("browser 与 driver 只能传入一个")
        if browser is None and driver is None:
            raise ValueError("必须传入 browser 或 driver")

        self.browser = browser
        self.username = username
        self.password = password
        self.name = name
        self.driver = driver or SeleniumWebDriver(browser)
        if self.business_cls is None:
            raise RuntimeError(f"{type(self).__name__} 未绑定业务类 business_cls")
        self.business = self.business_cls(self.driver)

    def __getattr__(self, name: str):
        # 仅在常规属性查找失败时触发；business 尚未赋值时直接报错避免递归
        if name == "business":
            raise AttributeError(name)
        return getattr(self.business, name)

    @property
    def platform(self) -> str:
        return self.driver.platform_name

    @property
    def aw(self):
        """基础操作入口 = 业务层实例（继承了端 base 与公共引擎）。"""
        return self.business

    @property
    def biz(self):
        """业务层的短别名，等价于 ``self.business``。"""
        return self.business

    def open(self, url: str) -> None:
        if self.browser is None:
            raise RuntimeError("Android 实机不支持 open(url)；请通过 adb 启动或操作应用")
        self.browser.get(url)

    def close(self) -> None:
        if self.browser is not None:
            self.browser.quit()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(username={self.username!r}, name={self.name!r})"


class TTUser(User):
    """TidiTree 项目测试用户（web 端）。"""

    business_cls = TidiTreeBusiness


class AndroidUser(User):
    """安卓项目测试用户（android 端；智能音箱屏系统，项目名待定）。"""

    business_cls = AndroidBusiness


class SwanUser(User):
    """Swan 项目测试用户（flutter 端）。"""

    business_cls = SwanBusiness

    @property
    def phone(self) -> str:
        """当前账号手机号（环境变量 SWAN_PHONE）。"""
        import os

        return os.environ.get("SWAN_PHONE", "").strip()
