# -*- coding: utf-8 -*-
"""Swan 回归·L11(设备管理与配网)专属业务 mixin。

本包大量用例落在「添加设备页 / 蓝牙·WiFi 配网页 / 设备设置页」等尚未
沉淀图像模板的未探索页面上，通用做法是 OCR 多候选锚点 + 分支探测。
本 mixin 只组合基础 AW 层原语(find_text_by_ocr / ocr_scan_page /
click_image / tap / press_back / find_image / sleep 等)，不调用业务层
方法，避免与既有 mixin 耦合；挂入 SwanBusiness MRO 后由 self.userA
直接调用。方法均满足 ≥2 处复用或多步编排的沉淀门槛。

红线提醒(供挂接方与本包用例共同遵守)：
- 禁区 1：固件升级只做「检查」与结果文案断言，全程禁点任何升级执行控件；
- 禁区 3：真实凭据写入(WiFi 配网提交)只允许在专用靶机轮次执行；
- 禁区 7：updateDeviceName 端口层校验只到「保存被拒/不保存」为止，
  绝不提交合法新名；
- 绑定真机音量/恢复出厂等写操作只到弹层为止，取消收尾。
"""
import os
import time

from image.image_name_mapping import SWAN_DEVICE_ADD_BTN


class SwanRM11Mixin:
    """L11 设备管理与配网编排：添加设备页/配网页/设备设置页的复用导航与探测。"""

    def bound_device_name(self) -> str:
        """绑定真机设备名：读运行环境变量 SWAN_DEVICE_NAME，缺省回退当前标定机名。"""
        return os.environ.get("SWAN_DEVICE_NAME", "Libretto_0E00")

    # ---------- OCR 多候选探测原语 ----------

    def _ocr_hit(self, texts) -> str:
        """单次全量 OCR 中按候选顺序查找(子串匹配，同 find_text_by_ocr 口径)，返回命中文案或 None。"""
        page_texts = [item.get("text") or "" for item in self.ocr_scan_page()]
        for text in texts:
            for page_text in page_texts:
                if page_text.strip() and text.lower() in page_text.lower():
                    return text
        return None

    def assert_any_ocr(self, texts, timeout: int = 10) -> str:
        """断言任一候选文案在当前页出现(带 deadline 轮询，适配加载慢的未探索页)。"""
        end_time = time.time() + max(timeout, 2)
        while True:
            hit = self._ocr_hit(texts)
            if hit is not None:
                return hit
            if time.time() >= end_time:
                break
            self.sleep(0.5)
        assert False, f"断言失败: 未出现任一候选文案 {list(texts)}"

    def probe_any_ocr(self, texts, timeout: int = 4):
        """探测任一候选文案是否出现；返回命中文案，全未命中返回 None(不断言，供分支判断)。"""
        end_time = time.time() + max(timeout, 1)
        while True:
            hit = self._ocr_hit(texts)
            if hit is not None:
                return hit
            if time.time() >= end_time:
                return None
            self.sleep(0.5)

    def click_first_ocr(self, texts, timeout: int = 6):
        """按候选顺序探测并点击首个命中文案；返回命中文案，全未命中返回 None(不断言)。"""
        end_time = time.time() + max(timeout, 1)
        while True:
            for text in texts:
                pos = self.find_text_by_ocr(text, timeout=1)
                if pos is not None:
                    self.tap(pos[0], pos[1])
                    return text
            if time.time() >= end_time:
                return None
            self.sleep(0.3)

    # ---------- 添加设备页 / 配网页导航 ----------

    def open_add_device_page(self) -> None:
        """设备页 → 点右上角「添加设备」[图] 进入添加设备页，断言蓝牙/WiFi 双卡片锚点。"""
        self.click_image(SWAN_DEVICE_ADD_BTN, timeout=10)
        self.assert_any_ocr(("蓝牙添加", "WiFi 添加", "蓝牙", "Wi-Fi"), timeout=10)

    def assert_ble_scanning(self) -> None:
        """断言蓝牙配网页处于扫描态(扫描指示文案可见，扫描启动允许数秒延迟)。"""
        self.assert_any_ocr(("正在扫描", "扫描中", "扫描附近的设备", "扫描"), timeout=15)

    def open_ble_provisioning(self) -> None:
        """添加设备页 → 点「蓝牙添加」卡片进入蓝牙配网页并断言扫描态。"""
        self.open_add_device_page()
        hit = self.click_first_ocr(("蓝牙添加", "蓝牙"), timeout=8)
        assert hit is not None, "添加设备页未找到「蓝牙添加」卡片"
        self.assert_ble_scanning()

    def open_wifi_provisioning(self) -> None:
        """添加设备页 → 点「WiFi 添加」卡片进入 WiFi 配网流程页并断言页面锚点。"""
        self.open_add_device_page()
        hit = self.click_first_ocr(("WiFi 添加", "WiFi添加", "Wi-Fi 添加", "WiFi"), timeout=8)
        assert hit is not None, "添加设备页未找到「WiFi 添加」卡片"
        self.assert_any_ocr(("热点", "Wi-Fi", "WiFi", "网络", "连接"), timeout=10)

    def back_to_device_page(self) -> None:
        """逐级返回键退出配网/添加流程回到设备页(每次返回前先探测，最多退 3 级)。"""
        for _ in range(3):
            if self.find_image(SWAN_DEVICE_ADD_BTN, timeout=3) is not None:
                return
            self.press_back()
        assert self.find_image(SWAN_DEVICE_ADD_BTN, timeout=3) is not None, \
            "连按返回仍未回到设备页(右上角添加设备按钮不可见)"

    # ---------- 设备设置页导航(设备名行 = 设置入口) ----------

    def open_device_settings_page(self) -> bool:
        """设备页 → 点绑定真机卡片设备名行(设置入口)进入设备设置页。

        区域限定设备卡片列表，避开底部播放条上的同名设备名；
        设备卡片不可见(离线/未绑)返回 False，由用例决定 skip。
        """
        pos = self.find_text_by_ocr(self.bound_device_name(), timeout=10,
                                    region=(0, 150, 720, 1150))
        if pos is None:
            return False
        self.tap(pos[0], pos[1])
        self.assert_any_ocr((self.bound_device_name(), "改名", "网络设置",
                             "恢复出厂", "固件", "参数"), timeout=10)
        return True

    def open_rename_page(self) -> bool:
        """设备设置页 → 点「改名」进入改名页并断言预填当前设备名；入口未找到返回 False。"""
        if self.click_first_ocr(("改名", "重命名", "设备名称"), timeout=6) is None:
            return False
        self.assert_any_ocr((self.bound_device_name(),), timeout=8)
        return True

    def open_firmware_page(self):
        """设备设置页 → 点固件/检查更新入口并断言落到固件页；入口未找到返回 None。

        红线：仅进入检查页；后续断言绝不点击任何升级执行控件(禁区 1)。
        """
        hit = self.click_first_ocr(("检查更新", "固件升级", "固件信息",
                                    "固件更新", "固件", "关于与升级"), timeout=8)
        if hit is None:
            return None
        self.assert_any_ocr(("检查更新", "当前版本", "版本", "升级"), timeout=8)
        return hit
