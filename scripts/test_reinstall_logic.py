"""
验证四种场景的重装逻辑，mock 掉 MuMu 和 APK 操作
"""
import sys
sys.path.insert(0, r"E:\UIAutotest")

from unittest.mock import patch, MagicMock
import utils.devices as dev_mod

# mock find_latest_apk_by_branch 返回值
def mock_find(keyword):
    if keyword == "":
        return ("http://server/release_4.23.5_9118.apk", "origin/release_4.23.5", "build=9118")
    else:
        return (f"http://server/{keyword}_9100.apk", f"origin/{keyword}", f"keyword={keyword}")

scenarios = [
    ("场景1: 本地默认（无 --reinstall）",    False, None),
    ("场景2: Jenkins REINSTALL=否",          False, None),
    ("场景3: Jenkins REINSTALL=是 指定分支", True,  "release_4.23.5"),
    ("场景4: Jenkins REINSTALL=是 最新包",   True,  ""),   # latest_online → ""
]

with patch.object(dev_mod, "find_latest_apk_by_branch", side_effect=mock_find), \
     patch.object(dev_mod, "download_apk", return_value="/tmp/popo.apk"), \
     patch.object(dev_mod, "install_apk_to_all_devices"), \
     patch.object(dev_mod, "is_mumu_running", return_value=False), \
     patch.object(dev_mod, "start_emulator", return_value=True), \
     patch.object(dev_mod, "adb_connect", return_value=True), \
     patch.object(dev_mod, "wait_device_ready", return_value=True), \
     patch.object(dev_mod, "set_window_size_and_arrange"), \
     patch("utils.window_manager.WindowManager.focus_window"):

    import time
    with patch.object(time, "sleep"):   # 跳过所有 sleep

        for title, reinstall, branch in scenarios:
            print(f"\n{'='*55}")
            print(f"  {title}")
            print(f"  reinstall={reinstall}  branch={branch!r}")
            print(f"{'='*55}")

            dev_mod.install_apk_to_all_devices.reset_mock()
            dev_mod.find_latest_apk_by_branch.reset_mock()

            from utils.devices import start_devices
            start_devices(count=1, reinstall=reinstall, branch=branch)

            if dev_mod.install_apk_to_all_devices.called:
                call_keyword = dev_mod.find_latest_apk_by_branch.call_args[0][0]
                _, name, desc = mock_find(call_keyword)
                print(f"  结果: [重装] {name}  ({desc})")
            else:
                print(f"  结果: [不重装]")
