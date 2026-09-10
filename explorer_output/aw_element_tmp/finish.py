# -*- coding: utf-8 -*-
"""收尾：恢复设备状态（个人信息页 → 首页·推荐 Tab）+ 新模板真机冒烟验证。

冒烟内容：
1. click_image(SWAN_HOME_TAB_AI) 切到 AI 顶 Tab（验证 Tab 未选中态模板可定位）
2. 页面出现「添加更多AI角色」后 click_image(SWAN_HOME_AI_ROLE_SETTINGS)，
   dump 语义树确认落地页（图标按钮无文案，需实测去向）
3. press_back 返回，click_image(SWAN_HOME_TAB_RECOMMEND) 切回推荐 Tab
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

from dotenv import load_dotenv  # noqa: E402

load_dotenv(r"E:\UIAutotest\.env.local")

from utils.aw.driver.flutter_driver import FlutterAndroidDriver  # noqa: E402
from utils.user import SwanUser  # noqa: E402
from utils.aw.business.swan import SwanBusiness as SB  # noqa: E402
from image.image_name_mapping import (  # noqa: E402
    SWAN_HOME_TAB_AI,
    SWAN_HOME_TAB_RECOMMEND,
    SWAN_HOME_AI_ROLE_SETTINGS,
    SWAN_HOME_AI_ADD_ROLE,
)

OUT = r"E:\UIAutotest\explorer_output\aw_element_tmp"


def main() -> None:
    user = SwanUser(driver=FlutterAndroidDriver())
    aw = user.aw

    # 1) 个人信息页 → 我的页 → 首页
    aw.press_back()
    time.sleep(1.0)
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=10), "返回后未到首页容器"
    user.go_home()
    print("[ok] 已回到首页容器")

    # 2) 冒烟：click_image 切 AI 顶 Tab
    assert aw.click_image(SWAN_HOME_TAB_AI, timeout=10), "click_image(SWAN_HOME_TAB_AI) 失败"
    time.sleep(2.0)
    assert aw.text_exists("添加更多AI角色", timeout=8), "AI Tab 生效断言失败（未出现入口文案）"
    print("[ok] SWAN_HOME_TAB_AI 模板真机点击生效")

    # 3) 角色设置图标按钮：click_image 并 dump 落地页
    assert aw.click_image(SWAN_HOME_AI_ROLE_SETTINGS, timeout=10), \
        "click_image(SWAN_HOME_AI_ROLE_SETTINGS) 失败"
    time.sleep(2.0)
    aw.take_screenshot(save_path=os.path.join(OUT, "smoke_ai_role_settings_page.png"))
    print("--- 落地页语义节点（前 25 个） ---")
    for n in aw.dump_semantics()[:25]:
        rid = (n.get("resource_id") or "").split("/")[-1]
        b = n.get("bounds")
        print(f"  id={rid!r} text={n.get('text')!r} desc={n.get('content_desc')!r} "
              f"click={n.get('clickable')} box={b}")
    aw.press_back()
    time.sleep(1.5)

    # 4) 切回推荐顶 Tab，收尾状态 = 首页·推荐
    assert aw.click_image(SWAN_HOME_TAB_RECOMMEND, timeout=10), \
        "click_image(SWAN_HOME_TAB_RECOMMEND) 失败"
    time.sleep(1.5)
    aw.take_screenshot(save_path=os.path.join(OUT, "final_state.png"))
    print("[ok] 收尾：已登录，首页·推荐 Tab（final_state.png）")


if __name__ == "__main__":
    main()
