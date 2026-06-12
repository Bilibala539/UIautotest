# P0 长按消息菜单操作合并 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 8 个长按消息操作方法（`recall/copy/multi_select/translate/favorite/delete/pin/reply`）中结构相同的 3 步样板代码（长按 → 点菜单 → sleep）提取为私有 helper，使每个方法只保留差异化的前置/后置逻辑，并验证所有相关测试仍通过。

**Architecture:** 在 `MuMuBusiness` 中新增私有方法 `_longpress_and_select_menu_item(message_text, menu_item)` 封装 3 步样板。`reply_message` 和 `favorite_message` 逻辑特殊（回复需额外输入、收藏有重试逻辑），**保持不动**。其余 6 个方法改为调用 helper。`user.py` 无需修改（只是透传层）。

**Tech Stack:** Python, pytest, MuMu Android 模拟器，AWBase/MuMuBusiness 层

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|---|---|---|
| `utils/aw/business/mumu.py` | Modify | 新增 helper，重构 6 个方法 |
| `docs/AW方法总结与复用指南.md` | Modify | 更新第四章相关方法描述 |

---

## Task 1：新增私有 helper `_longpress_and_select_menu_item`

**Files:**
- Modify: `utils/aw/business/mumu.py`（在 `recall_message` 定义前，即第 1168 行附近的 `# ==================== 消息操作相关 ====================` 区块内插入）

- [ ] **Step 1：在 `mumu.py` 中 `recall_message` 方法（~1170 行）之前插入 helper**

  找到以下代码（行号约 1168）：
  ```python
      def recall_message(self, message_text: str):
  ```
  在其**前面**插入：
  ```python
      def _longpress_and_select_menu_item(self, message_text: str, menu_item: str) -> None:
          """长按消息文字，从弹出菜单中点击指定菜单项。

          被 recall/copy/delete/pin/multi_select/translate 等方法复用。
          前置条件: 当前在聊天页面。

          Args:
              message_text: 要长按的消息文字
              menu_item: 菜单项文字（如"撤回"/"复制"/"Pin"/"删除"/"多选"/"翻译"）
          """
          self.long_press_text(message_text, duration=1.5)
          time.sleep(1)
          self.click_text(menu_item, region=Normal.HALF_DOWN)
          time.sleep(1)

  ```

- [ ] **Step 2：确认插入无语法错误**

  ```bash
  cd E:\UIAutotest && python -c "from utils.aw.business.mumu import MuMuBusiness; print('OK')"
  ```
  期望输出: `OK`

---

## Task 2：重构 `recall_message`

**Files:**
- Modify: `utils/aw/business/mumu.py`（行约 1170–1223）

当前代码（关键部分）：
```python
msg_y = self.find_text_by_ocr(message_text)[1]
time.sleep(0.5)
self.long_press_text(message_text)
time.sleep(1)
self.click_text("撤回")
time.sleep(1)
if self.find_image(MSG_RECELL_POP, timeout=5):
    self.click_text("确定")
time.sleep(1)
verify_y_top = max(0, msg_y - 60)
verify_y_bottom = min(960, msg_y + 60)
self.text_exists("你撤回了一条消息", timeout=5, region=(0, verify_y_top, 540, verify_y_bottom))
```

- [ ] **Step 1：替换 recall_message 方法体**

  将方法体改为：
  ```python
  def recall_message(self, message_text: str):
      """
      撤回消息

      前置条件: 当前在聊天页面，消息为自己发送且24小时内。

      Args:
          message_text: 要撤回的消息文字内容

      Returns:
          bool: 撤回是否成功
      """
      logger.info(f"🔄 [MuMu] 撤回消息: '{message_text}'")
      msg_y = self.find_text_by_ocr(message_text)[1]
      time.sleep(0.5)
      self._longpress_and_select_menu_item(message_text, "撤回")
      if self.find_image(MSG_RECELL_POP, timeout=5):
          self.click_text("确定")
      time.sleep(1)
      verify_y_top = max(0, msg_y - 60)
      verify_y_bottom = min(960, msg_y + 60)
      self.text_exists("你撤回了一条消息", timeout=5,
                       region=(0, verify_y_top, 540, verify_y_bottom))
      logger.info(f"✅ [MuMu] 消息撤回成功: '{message_text}'")
      return True
  ```

---

## Task 3：重构 `copy_message`

**Files:**
- Modify: `utils/aw/business/mumu.py`（行约 1273–1307）

- [ ] **Step 1：替换 copy_message 方法体**

  ```python
  def copy_message(self, message_text: str) -> bool:
      """
      复制消息

      前置条件: 当前在聊天页面。

      Args:
          message_text: 要复制的消息文字

      Returns:
          bool: 复制是否成功
      """
      logger.info(f"📋 [MuMu] 复制消息: '{message_text}'")
      self._longpress_and_select_menu_item(message_text, "复制")
      self.image_exists(CHAT_COPY_SUCCESS_TOAST)
      logger.info(f"✅ [MuMu] 消息复制成功")
      return True
  ```

---

## Task 4：重构 `multi_select_message`

**Files:**
- Modify: `utils/aw/business/mumu.py`（行约 1309–1347）

- [ ] **Step 1：替换 multi_select_message 方法体**

  ```python
  def multi_select_message(self, message_text: str) -> bool:
      """
      进入多选模式

      前置条件: 当前在聊天页面。

      Args:
          message_text: 触发多选的消息文字

      Returns:
          bool: 多选模式进入和退出是否成功
      """
      logger.info(f"☑️ [MuMu] 多选消息: '{message_text}'")
      self._longpress_and_select_menu_item(message_text, "多选")
      self.image_exists(CHAT_MULTI_SELECT_TITLE, region=Normal.HALF_UP)
      self.press_back()
      time.sleep(0.5)
      logger.info(f"✅ [MuMu] 多选模式进入和退出成功")
      return True
  ```

---

## Task 5：重构 `translate_message`

**Files:**
- Modify: `utils/aw/business/mumu.py`（行约 1349–1393）

原代码用 `long_press(pos[0], pos[1])` 而非 `long_press_text`（因已有坐标）；重构后改用 helper（`long_press_text` 内部也做 OCR，对坐标结果完全一致），额外 2s 等待通过在 helper 调用后再 sleep 补齐（helper 内已有 1s，翻译原本等 3s）。

- [ ] **Step 1：替换 translate_message 方法体**

  ```python
  def translate_message(self, message_text: str) -> bool:
      """
      翻译消息

      前置条件: 当前在聊天页面。

      Args:
          message_text: 要翻译的消息文字

      Returns:
          bool: 翻译是否成功
      """
      logger.info(f"🌐 [MuMu] 翻译消息: '{message_text}'")
      msg_pos = self.find_text_by_ocr(message_text, timeout=10)
      assert msg_pos is not None, f"未找到消息文字 '{message_text}'"
      msg_y = msg_pos[1]
      self._longpress_and_select_menu_item(message_text, "翻译")
      time.sleep(2)  # 翻译接口响应较慢，在 helper 1s 基础上再等 2s
      search_y1 = max(0, msg_y - 100)
      search_y2 = min(960, msg_y + 100)
      self.image_exists(CHAT_TRANSLATE_RESULT, timeout=15,
                        region=(0, search_y1, 540, search_y2 - search_y1))
      logger.info(f"✅ [MuMu] 消息翻译成功")
      return True
  ```

---

## Task 6：重构 `delete_message`

**Files:**
- Modify: `utils/aw/business/mumu.py`（行约 3001–3042）

- [ ] **Step 1：替换 delete_message 方法体**

  ```python
  def delete_message(self, message_text: str) -> bool:
      """
      删除消息

      前置条件: 当前在聊天页面。

      Args:
          message_text: 要删除的消息文字内容

      Returns:
          bool: 删除是否成功
      """
      logger.info(f"🗑️ [MuMu] 删除消息: '{message_text}'")
      self._longpress_and_select_menu_item(message_text, "删除")
      self.find_text_by_ocr("确认删除消息", timeout=3)
      self.click_text("删除", timeout=3)
      time.sleep(1)
      logger.info(f"✅ [MuMu] 消息删除成功: '{message_text}'")
      return True
  ```

---

## Task 7：重构 `pin_message`

**Files:**
- Modify: `utils/aw/business/mumu.py`（行约 3044–3077）

- [ ] **Step 1：替换 pin_message 方法体**

  ```python
  def pin_message(self, message_text: str) -> bool:
      """
      Pin 消息（置顶消息）

      前置条件: 当前在聊天页面。

      Args:
          message_text: 要 Pin 的消息文字内容

      Returns:
          bool: Pin 是否成功
      """
      logger.info(f"📌 [MuMu] Pin消息: '{message_text}'")
      self._longpress_and_select_menu_item(message_text, "Pin")
      logger.info(f"✅ [MuMu] 消息Pin成功: '{message_text}'")
      return True
  ```

---

## Task 8：语法校验 + 整体 import 检查

- [ ] **Step 1：验证 mumu.py 无语法错误**

  ```bash
  cd E:\UIAutotest && python -c "from utils.aw.business.mumu import MuMuBusiness; print('syntax OK')"
  ```
  期望: `syntax OK`

- [ ] **Step 2：验证 user.py 委托层无需修改（确认签名未变）**

  ```bash
  cd E:\UIAutotest && python -c "from utils.user import PPUser; print('user.py OK')"
  ```
  期望: `user.py OK`

---

## Task 9：更新 AW 方法指南

**Files:**
- Modify: `docs/AW方法总结与复用指南.md`（第四章 4.4 ~ 4.4e 区域，以及 reply_message / favorite_message 小节）

- [ ] **Step 1：在 4.4 小节（撤回消息）前新增 "内部实现说明" 段落**

  在第四章 `### 4.4 🔄 撤回消息` 之前，插入以下说明：

  ```markdown
  ### 4.4（内部实现）`_longpress_and_select_menu_item(message_text, menu_item)`

  **私有 helper，外部用例请勿直接调用。**

  所有简单长按菜单操作（撤回/复制/多选/翻译/删除/Pin）的公共 3 步样板：
  1. `long_press_text(message_text, duration=1.5)` — 长按消息气泡
  2. `time.sleep(1)` — 等待菜单弹出
  3. `click_text(menu_item, region=HALF_DOWN)` — 点击菜单项
  4. `time.sleep(1)` — 等待响应

  **注意：** `reply_message` 和 `favorite_message` 逻辑特殊，**未使用此 helper**。

  ---
  ```

- [ ] **Step 2：在各方法描述中补注 "内部调用 helper"**

  在 4.4（撤回）、4.4b（复制）、4.4c（多选）、4.4d（翻译）的流程说明中，将步骤 1-2（长按+等待菜单）替换为：
  ```
  1. `_longpress_and_select_menu_item(message_text, "操作名")` — 长按并点击菜单
  ```

---

## Task 10：运行受影响的测试用例

- [ ] **Step 1：运行所有受影响的 checklist 和 session_msg 测试**

  ```bash
  cd E:\UIAutotest && python -m pytest \
    tests/checklist/test_删除消息.py \
    tests/checklist/test_回复消息.py \
    tests/checklist/test_复制消息.py \
    tests/checklist/test_多选消息.py \
    tests/checklist/test_收藏消息.py \
    tests/checklist/test_翻译消息.py \
    tests/session_msg/test_标签页_Pin_tab自动显示.py \
    tests/checklist/test_P2P发送文本文件.py \
    tests/checklist/test_P2P发送视频文件.py \
    -v --tb=short 2>&1 | tail -50
  ```

  期望：所有用例 PASSED。若有失败，参考归因顺序（图片质量 → 代码逻辑）排查。

- [ ] **Step 2：若测试全通过，commit**

  ```bash
  cd E:\UIAutotest && git add utils/aw/business/mumu.py docs/AW方法总结与复用指南.md && git commit -m "refactor: 提取长按消息菜单公共 helper，消除 P0 冗余"
  ```

---

## 不在本次范围内（保持不变）

- `reply_message` — 有额外 `input_text` + `send` 步骤，结构不同
- `favorite_message` — 有重试循环 + 复杂 OCR 检测逻辑，结构不同
- `user.py` — 只是透传委托层，无样板冗余
- P1/P2 集群（群设置/群管理/群公告/二维码/图片编辑）— 下一轮处理
