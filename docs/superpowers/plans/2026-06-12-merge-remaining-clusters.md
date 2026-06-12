# 剩余集群冗余合并 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 合并 mumu.py 中 P0/P1/P2 四个冗余集群（重复群公告、scroll-find 模式、群二维码、图片编辑入口），删除或提取样板代码，使每个方法只保留差异逻辑，并验证所有受影响测试通过。

**Architecture:**
- 集群 4（群公告）：删除 `open_group_announcement`，将其验证逻辑合入 `open_group_announcement_page`
- 集群 2+3（scroll-find）：新增 `_scroll_find_and_act` 私有 helper，6 个公开方法改用它；删除无调用者的 2 个冗余方法；`check_group_message_reminder` 改为调用 `toggle_group_setting_switch` 的 1 行委托
- 集群 5（二维码）：`open_group_qr_code` 加 `stay=False` 参数，删除 `click_group_qr_code`；user.py 中的 `click_group_qr_code` 改为委托到 `open_group_qr_code(stay=True)`
- 集群 6（图片编辑）：新增 `_open_first_album_image` 私有 helper，5 个方法共用它

**Tech Stack:** Python, pytest, UIAutotest AWBase/MuMuBusiness 框架

---

## 文件变更清单

| 文件 | 操作 | 涉及方法 |
|---|---|---|
| `utils/aw/business/mumu.py` | Modify | 见各 Task |
| `utils/user.py` | Modify | Task 2（二维码 click 委托） |
| `docs/AW方法总结与复用指南.md` | Modify | Task 5（文档更新） |

---

## Task 1：P0 集群4 — 合并重复的群公告方法

**Files:**
- Modify: `utils/aw/business/mumu.py`（行约 4186–4246）

两个方法对比：
- `open_group_announcement`（行 4186–4214）：进入群设置→点群公告→验证（占位图或"编辑"文字）→**停留**
- `open_group_announcement_page`（行 4216–4246）：进入群设置→点群公告→截图→`return_to_message_list()`

策略：删除 `open_group_announcement`，把其验证逻辑加入 `open_group_announcement_page`。

- [ ] **Step 1：找到 `open_group_announcement_page` 的 `self.click_text("群公告", timeout=5)` + `time.sleep(1.5)` 那两行之后、`self.take_screenshot(...)` 之前，插入验证逻辑**

  定位 `open_group_announcement_page` 方法，找到：
  ```python
          self.click_text("群公告", timeout=5)
          time.sleep(1.5)

          self.take_screenshot(
  ```
  在 `time.sleep(1.5)` 和 `self.take_screenshot(` 之间插入：
  ```python
          if self.find_image(GROUP_ANNOUNCEMENT_EMPTY_PLACEHOLDER, timeout=2):
              logger.info("✅ 群公告页为空占位符已出现")
          else:
              self.find_text_by_ocr("编辑", timeout=3)

  ```

- [ ] **Step 2：删除整个 `open_group_announcement` 方法**

  删除从 `    def open_group_announcement(self, group_identifier: str) -> bool:` 到其 `return True` 的整个方法体（约行 4186–4214）

- [ ] **Step 3：语法校验**

  ```bash
  cd E:\UIAutotest && python -c "from utils.aw.business.mumu import MuMuBusiness; print('OK')"
  ```
  期望：`OK`

- [ ] **Step 4：Commit**

  ```bash
  cd E:\UIAutotest && git add utils/aw/business/mumu.py && git commit -m "refactor: 合并重复群公告方法，删除 open_group_announcement

  Co-Authored-By: Claude Sonnet 4.6 (1M context) <noreply@anthropic.com>"
  ```

---

## Task 2：P2 集群5 — 合并重复的群二维码方法

**Files:**
- Modify: `utils/aw/business/mumu.py`（行约 4144–4184 和 4430–4458）
- Modify: `utils/user.py`（行约 743–744）

两个方法对比：
- `open_group_qr_code`（行 4144）：进入群设置→点二维码入口→验证"有效"→`press_back()`→验证"群公告"
- `click_group_qr_code`（行 4430）：进入群设置→点二维码入口→验证"有效"→**停留**

策略：`open_group_qr_code` 加 `stay: bool = False` 参数；删除 `click_group_qr_code`；user.py 中 `click_group_qr_code` 改为委托。

- [ ] **Step 1：修改 `open_group_qr_code` 方法签名和末尾逻辑**

  找到 `open_group_qr_code` 方法，将：
  ```python
      def open_group_qr_code(self, group_identifier: str) -> bool:
  ```
  改为：
  ```python
      def open_group_qr_code(self, group_identifier: str, stay: bool = False) -> bool:
  ```

  找到方法末尾：
  ```python
          self.find_text_by_ocr("有效", timeout=5, region=Normal.HALF_UP)

          logger.info("✅ [MuMu] 已打开群二维码页面")
          # 返回群设置页面
          self.press_back()
          time.sleep(1)
          self.text_exists("群公告", timeout=5)
          return True
  ```
  改为：
  ```python
          self.find_text_by_ocr("有效", timeout=5, region=Normal.HALF_UP)
          logger.info("✅ [MuMu] 已打开群二维码页面")
          if not stay:
              self.press_back()
              time.sleep(1)
              self.text_exists("群公告", timeout=5)
          return True
  ```

- [ ] **Step 2：删除整个 `click_group_qr_code` 方法**

  删除从 `    def click_group_qr_code(self, group_identifier: str) -> bool:` 到 `return True` 的整个方法体（约行 4430–4458）

- [ ] **Step 3：修改 `utils/user.py` 中的 `click_group_qr_code` 委托**

  找到 user.py 中（约行 743）：
  ```python
      def click_group_qr_code(self, group_identifier: str) -> bool:
          return self.aw.click_group_qr_code(group_identifier)
  ```
  改为：
  ```python
      def click_group_qr_code(self, group_identifier: str) -> bool:
          return self.aw.open_group_qr_code(group_identifier, stay=True)
  ```

- [ ] **Step 4：语法校验**

  ```bash
  cd E:\UIAutotest && python -c "from utils.aw.business.mumu import MuMuBusiness; from utils.user import PPUser; print('OK')"
  ```
  期望：`OK`

- [ ] **Step 5：Commit**

  ```bash
  cd E:\UIAutotest && git add utils/aw/business/mumu.py utils/user.py && git commit -m "refactor: 合并重复群二维码方法，open_group_qr_code 加 stay 参数

  Co-Authored-By: Claude Sonnet 4.6 (1M context) <noreply@anthropic.com>"
  ```

---

## Task 3：P1 集群2+3 — scroll-find 模式合并（最大 Task）

**Files:**
- Modify: `utils/aw/business/mumu.py`（多处）

### 新增 helper（插入位置：`click_in_group_settings` 定义前）

找到 `click_in_group_settings` 方法定义处，在其**之前**插入：

```python
    def _scroll_find_and_act(self, item_name: str, action: str = 'verify',
                              verify_text: str = None, dx: int = 200,
                              region=None, max_screens: int = 5) -> dict:
        """
        在当前页面滚动查找指定文字，然后执行指定操作。

        调用前需先导航到目标页面（此方法不负责导航和返回）。

        Args:
            item_name: 要查找的文字标签
            action: 'verify'=仅查找验证, 'click'=找到后点击, 'toggle'=找到后点击右侧开关
            verify_text: action='click' 时，点击后在新页面验证此文字（可选）
            dx: action='toggle' 时，开关相对文字的 x 偏移（默认 200）
            region: 查找区域限制（可选）
            max_screens: 最大滚动屏数

        Returns:
            dict: {found, position, screen_index, item_name}
        """
        found = False
        position = None
        screen_index = None

        for screen in range(max_screens):
            pos = self.find_text_by_ocr(item_name, timeout=2, region=region)
            if not pos and region is not None:
                pos = self.find_text_by_ocr(item_name, timeout=2)
            if pos:
                found = True
                position = pos
                screen_index = screen
                if action == 'click':
                    self.tap(pos[0], pos[1])
                    time.sleep(1.5)
                    if verify_text:
                        assert self.find_text_by_ocr(verify_text, timeout=5), \
                            f"点击 '{item_name}' 后未找到 '{verify_text}'"
                elif action == 'toggle':
                    self.tap(pos[0] + dx, pos[1])
                    time.sleep(1)
                break
            self.swipe_up(300)
            time.sleep(0.5)

        return {
            'found': found,
            'position': position,
            'screen_index': screen_index,
            'item_name': item_name,
        }

```

### 重构 `verify_group_setting_default`

找到现有方法（约行 4054-4097），将方法体替换为：

```python
    def verify_group_setting_default(self, group_name_keyword: str, setting_name: str) -> str:
        """
        验证群设置页面中某个设置项是否存在，截图记录状态。

        Args:
            group_name_keyword: 群名关键词
            setting_name: 设置项名称

        Returns:
            str: "found" 表示找到
        """
        logger.info(f"🔍 [MuMu] 验证群设置: {setting_name}")
        self._ensure_message_page()
        self._enter_group_settings(group_name_keyword)
        result = self._scroll_find_and_act(setting_name, 'verify')
        assert result['found'], f"群设置页面中未找到 '{setting_name}'"
        self.take_screenshot(
            save_path=f'E:\\UIAutotest\\explorer_output\\screenshots\\group_setting_{setting_name}.png'
        )
        self.return_to_message_list()
        logger.info(f"✅ [MuMu] 群设置 '{setting_name}' 验证完成")
        return "found"
```

### 删除 `check_group_settings_item`

删除整个 `check_group_settings_item` 方法（约行 4099–4142）。该方法在 mumu.py 外部无调用者，user.py 中也无委托。

### 重构 `check_group_message_reminder` 为 1 行委托

找到现有方法（约行 4015-4052），将方法体替换为：

```python
    def check_group_message_reminder(self, group_name_keyword: str) -> bool:
        """切换群消息提醒开关（委托给 toggle_group_setting_switch）"""
        return self.toggle_group_setting_switch(group_name_keyword, "消息提醒")
```

注意：`toggle_group_setting_switch` 定义在本类中（见下文），`check_group_message_reminder` 调用它时对象已初始化，无循环依赖。

### 重构 `click_in_group_settings`

找到现有方法（约行 4250-4298），将方法体替换为：

```python
    def click_in_group_settings(self, group_identifier: str, click_text: str,
                                verify_text: str = None, region=None) -> bool:
        """
        进入群设置后点击指定文字项，并可选验证新页面。

        Args:
            group_identifier: 群关键词
            click_text: 要点击的文字
            verify_text: 点击后新页面应包含的文字（可选）
            region: 查找区域限制（可选）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"👆 [MuMu] 群设置中点击 '{click_text}' (验证: {verify_text})")
        self._enter_group_settings(group_identifier)
        result = self._scroll_find_and_act(click_text, 'click',
                                           verify_text=verify_text, region=region)
        assert result['found'], f"群设置页面未找到 '{click_text}'"
        self.return_to_message_list()
        return True
```

### 重构 `toggle_group_setting_switch`

找到现有方法（约行 4300-4340），将方法体替换为：

```python
    def toggle_group_setting_switch(self, group_identifier: str, setting_name: str,
                                    dx: int = 200) -> bool:
        """
        切换群设置页中某开关。

        Args:
            group_identifier: 群关键词
            setting_name: 开关对应的文字标签
            dx: 开关相对文字的x偏移（默认+200，开关在右侧）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🔀 [MuMu] 切换群设置开关 '{setting_name}'")
        self._enter_group_settings(group_identifier)
        result = self._scroll_find_and_act(setting_name, 'toggle', dx=dx)
        assert result['found'], f"群设置页面未找到 '{setting_name}'"
        self.return_to_message_list()
        return True
```

### 重构 `verify_in_group_management`

找到现有方法（约行 4714-4750），将方法体替换为：

```python
    def verify_in_group_management(self, group_identifier: str, setting_name: str) -> str:
        """
        进入群管理子页面，查找指定设置项。

        Args:
            group_identifier: 群关键词
            setting_name: 设置项名称（如"转让群主"/"群管理员"/"解散群组"）

        Returns:
            str: "found" 表示找到
        """
        logger.info(f"🔍 [MuMu] 在群管理中查找 '{setting_name}'")
        self.enter_group_management(group_identifier)
        result = self._scroll_find_and_act(setting_name, 'verify')
        assert result['found'], f"群管理页面中未找到 '{setting_name}'"
        self.return_to_message_list()
        logger.info(f"✅ 验证 '{setting_name}' 完成")
        return "found"
```

### 重构 `click_in_group_management`

找到现有方法（约行 4752-4788），将方法体替换为：

```python
    def click_in_group_management(self, group_identifier: str, click_text: str,
                                  verify_text: str = None) -> bool:
        """
        进入群管理页后点击指定项，验证新页面。

        Args:
            group_identifier: 群关键词
            click_text: 要点击的文字
            verify_text: 点击后新页面应包含的文字（可选）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"👆 [MuMu] 群管理中点击 '{click_text}' (验证: {verify_text})")
        self.enter_group_management(group_identifier)
        result = self._scroll_find_and_act(click_text, 'click', verify_text=verify_text)
        assert result['found'], f"群管理页未找到 '{click_text}'"
        self.return_to_message_list()
        return True
```

### 重构 `toggle_group_management_switch`

找到现有方法（约行 4790-4822），将方法体替换为：

```python
    def toggle_group_management_switch(self, group_identifier: str, setting_name: str,
                                       dx: int = 200) -> bool:
        """
        在群管理页切换开关。

        Args:
            group_identifier: 群关键词
            setting_name: 开关名称
            dx: 开关相对文字的x偏移

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🔀 [MuMu] 群管理切换开关 '{setting_name}'")
        self.enter_group_management(group_identifier)
        result = self._scroll_find_and_act(setting_name, 'toggle', dx=dx)
        assert result['found'], f"群管理页未找到 '{setting_name}'"
        self.return_to_message_list()
        logger.info(f"✅ 开关已切换")
        return True
```

- [ ] **Step 1：插入 `_scroll_find_and_act` helper（在 `click_in_group_settings` 定义前）**

- [ ] **Step 2：重构 `verify_group_setting_default`**

- [ ] **Step 3：删除 `check_group_settings_item`**

- [ ] **Step 4：重构 `check_group_message_reminder` 为 1 行委托**

- [ ] **Step 5：重构 `click_in_group_settings`**

- [ ] **Step 6：重构 `toggle_group_setting_switch`**

- [ ] **Step 7：重构 `verify_in_group_management`**

- [ ] **Step 8：重构 `click_in_group_management`**

- [ ] **Step 9：重构 `toggle_group_management_switch`**

- [ ] **Step 10：语法校验**

  ```bash
  cd E:\UIAutotest && python -c "from utils.aw.business.mumu import MuMuBusiness; print('OK')"
  ```
  期望：`OK`

- [ ] **Step 11：Commit**

  ```bash
  cd E:\UIAutotest && git add utils/aw/business/mumu.py && git commit -m "refactor: 提取 _scroll_find_and_act helper，合并群设置/群管理 scroll-find 模式

  Co-Authored-By: Claude Sonnet 4.6 (1M context) <noreply@anthropic.com>"
  ```

---

## Task 4：P2 集群6 — 图片编辑入口合并

**Files:**
- Modify: `utils/aw/business/mumu.py`（多处）

5 个方法共享以下入口：
```python
self.click_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
time.sleep(1)
self.click_image(CHAT_PLUS_ALBUM, region=Normal.HALF_DOWN)
time.sleep(2)
self.tap(70, 200)
time.sleep(1.5)
```

新增私有 helper `_open_first_album_image()`，并重构 `send_image` / `select_edit_send_image_from_album` / `select_edit_with_tools_send_image` / `enter_image_editor_from_album` / `edit_image_done_check_popup`。

### 插入位置：在 `send_image` 定义前（约行 2436）

```python
    def _open_first_album_image(self) -> None:
        """
        打开 + 面板 → 点相册 → 点击第一张图片进入预览。

        调用前提: 当前在聊天页面（有加号按钮可见）。
        退出状态: 已点击相册网格第一张图片，预览界面即将出现。

        注: 坐标 (70, 200) 基于 540×960 分辨率相册网格第一行第一张缩略图，
        不可使用模板匹配（内容动态变化）。
        """
        self.click_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)
        self.click_image(CHAT_PLUS_ALBUM, region=Normal.HALF_DOWN)
        time.sleep(2)
        self.tap(70, 200)
        time.sleep(1.5)

```

### 重构 `send_image`（约行 2436–2467）

```python
    def send_image(self) -> bool:
        """
        从相册选择第一张图片并发送（不编辑）。

        前置条件: 当前在聊天页面。
        """
        self._open_first_album_image()
        self.click_text("发送", region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        logger.info("[MuMu] 图片发送成功")
        return True
```

### 重构 `select_edit_send_image_from_album`（约行 2495–2556）

```python
    def select_edit_send_image_from_album(self, recipient: str) -> bool:
        """
        从相册选图 → 进入预览 → 点击"编辑" → 在编辑器中完成 → 发送。

        Args:
            recipient: 收件人账号

        Returns:
            bool: 是否成功完成编辑并发送
        """
        logger.info(f"[MuMu] 从相册选图编辑后发送给: {recipient}")
        self._enter_chat_page(recipient)
        self._open_first_album_image()
        self.click_image(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1.5)
        self.image_exists(IMAGE_EDITOR_TOOLBAR, region=Normal.HALF_DOWN, timeout=8)
        logger.info("[MuMu] 已进入图片编辑器")
        self.click_text("完成")
        time.sleep(1)
        self.image_exists(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=5)
        self.click_image(ALBUM_PREVIEW_SEND_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        logger.info("[MuMu] 相册选图编辑后发送成功")
        return True
```

### 重构 `select_edit_with_tools_send_image`（约行 2648–2702）

```python
    def select_edit_with_tools_send_image(self, recipient: str) -> bool:
        """
        从相册选图 → 编辑器中使用画笔工具绘制 → 完成 → 发送。

        Args:
            recipient: 收件人账号

        Returns:
            bool: 是否成功
        """
        logger.info(f"[MuMu] 从相册选图，使用工具编辑后发送给: {recipient}")
        self._enter_chat_page(recipient)
        self._open_first_album_image()
        self.click_image(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1.5)
        self.image_exists(IMAGE_EDITOR_TOOLBAR, region=Normal.HALF_DOWN, timeout=8)
        self.swipe(150, 400, 380, 400, duration=0.5)
        time.sleep(0.5)
        self.click_text("完成")
        time.sleep(1)
        self.image_exists(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=5)
        self.click_image(ALBUM_PREVIEW_SEND_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        logger.info("[MuMu] 使用工具编辑后发送成功")
        return True
```

### 重构 `enter_image_editor_from_album`（约行 5243–5278）

```python
    def enter_image_editor_from_album(self, recipient: str) -> bool:
        """
        进入图片编辑器（从相册选图路径），不执行后续操作。

        Returns:
            bool: 是否成功进入编辑器
        """
        logger.info(f"[MuMu] 进入图片编辑器（从相册）: {recipient}")
        popup_text = self.find_text_by_ocr("显示浮窗", timeout=2)
        if popup_text:
            logger.info("⚠️ 检测到浮窗权限弹窗，点击取消")
            self.tap(171, 577)
            time.sleep(1)
            if self.find_text_by_ocr("显示浮窗", timeout=2):
                self.tap(171, 577)
                time.sleep(1)
        self._enter_chat_page(recipient)
        self._open_first_album_image()
        self.click_text("编辑", timeout=10, region=Normal.HALF_DOWN)
        time.sleep(0.5)
        done_pos = self.find_text_by_ocr("完成", timeout=8)
        assert done_pos is not None, "未进入图片编辑器（未找到'完成'按钮）"
        logger.info("[MuMu] 已进入图片编辑器")
        return True
```

### 重构 `edit_image_done_check_popup`（约行 5297–5325）

```python
    def edit_image_done_check_popup(self, recipient: str) -> bool:
        """
        从相册进入编辑器 → 点击完成 → 验证弹出操作弹窗。

        Returns:
            bool: 是否弹出包含"发送给同事或群组"的操作弹窗
        """
        logger.info(f"[MuMu] 编辑图片完成后检查弹窗: {recipient}")
        self._enter_chat_page(recipient)
        self._open_first_album_image()
        self.click_text("编辑", timeout=10, region=Normal.HALF_DOWN)
        time.sleep(0.5)
        done_pos = self.find_text_by_ocr("完成", timeout=8)
        assert done_pos is not None, "未进入图片编辑器"
        self.click_text("完成")
        time.sleep(1.5)
        self.text_exists("发送给同事或群组")
        logger.info("[MuMu] 编辑完成弹窗验证通过")
        return True
```

- [ ] **Step 1：插入 `_open_first_album_image` helper（在 `send_image` 定义前）**

- [ ] **Step 2：重构 `send_image`**

- [ ] **Step 3：重构 `select_edit_send_image_from_album`**

- [ ] **Step 4：重构 `select_edit_with_tools_send_image`**

- [ ] **Step 5：重构 `enter_image_editor_from_album`**

- [ ] **Step 6：重构 `edit_image_done_check_popup`**

- [ ] **Step 7：语法校验**

  ```bash
  cd E:\UIAutotest && python -c "from utils.aw.business.mumu import MuMuBusiness; print('OK')"
  ```
  期望：`OK`

- [ ] **Step 8：Commit**

  ```bash
  cd E:\UIAutotest && git add utils/aw/business/mumu.py && git commit -m "refactor: 提取 _open_first_album_image helper，合并图片编辑入口重复路径

  Co-Authored-By: Claude Sonnet 4.6 (1M context) <noreply@anthropic.com>"
  ```

---

## Task 5：更新 AW 方法指南文档

**Files:**
- Modify: `docs/AW方法总结与复用指南.md`

- [ ] **Step 1：删除/合并群公告相关描述**

  找到文档中 `open_group_announcement` 和 `open_group_announcement_page` 的描述（第四章附近）：
  - 如果有独立的 `open_group_announcement` 小节，删除它
  - 在 `open_group_announcement_page` 描述中加一句："已集成验证逻辑（空占位图/编辑文字），原 `open_group_announcement` 已合并入此方法"

- [ ] **Step 2：更新群二维码描述**

  找到 `open_group_qr_code` 描述，在参数说明中加入：
  - `stay: bool = False` — 是否停留在二维码页（默认 False，即打开后返回群设置）
  - 说明原 `click_group_qr_code` 已合并，等效于 `open_group_qr_code(stay=True)`

- [ ] **Step 3：新增 `_scroll_find_and_act` 说明**

  在第四章 `### 4.12 群设置相关` 或类似区块之前，插入：

  ```markdown
  ### （内部实现）`_scroll_find_and_act(item_name, action, ...)`

  > **私有 helper，外部用例请勿直接调用。**

  所有"进入页面→逐屏滚动查找文字→执行操作→返回消息列表"的公共骨架。

  | `action` 值 | 行为 |
  |---|---|
  | `'verify'` | 仅查找，返回 found/position dict |
  | `'click'` | 找到后 `tap(pos)`，可选验证新页面 |
  | `'toggle'` | 找到后 `tap(pos[0]+dx, pos[1])` 切换开关 |

  **使用此 helper 的方法：**
  `verify_group_setting_default` / `click_in_group_settings` / `toggle_group_setting_switch` /
  `verify_in_group_management` / `click_in_group_management` / `toggle_group_management_switch`

  ---
  ```

- [ ] **Step 4：新增 `_open_first_album_image` 说明**

  在图片编辑方法区块前插入：

  ```markdown
  ### （内部实现）`_open_first_album_image()`

  > **私有 helper，外部用例请勿直接调用。**

  从聊天页面打开 + 面板 → 进入相册 → 点击第一张图片（坐标 (70,200)，基于 540×960 分辨率）。

  **使用此 helper 的方法：**
  `send_image` / `select_edit_send_image_from_album` / `select_edit_with_tools_send_image` /
  `enter_image_editor_from_album` / `edit_image_done_check_popup`

  ---
  ```

- [ ] **Step 5：Commit**

  ```bash
  cd E:\UIAutotest && git add "docs/AW方法总结与复用指南.md" && git commit -m "docs: 更新 AW 方法指南 — 记录剩余集群合并结果

  Co-Authored-By: Claude Sonnet 4.6 (1M context) <noreply@anthropic.com>"
  ```

---

## Task 6：运行受影响测试

- [ ] **Step 1：运行群公告相关测试（P0 集群4）**

  ```bash
  cd E:\UIAutotest && python -m pytest \
    tests/add/test_编辑公告入口.py \
    tests/checklist/test_无公告群主进入.py \
    tests/checklist/test_有公告群主进入.py \
    tests/checklist/test_群公告为空.py \
    -v --tb=short 2>&1
  ```

- [ ] **Step 2：运行群二维码相关测试（P2 集群5）**

  ```bash
  cd E:\UIAutotest && python -m pytest \
    "tests/add/test_允许加群关闭_分享二维码.py" \
    tests/checklist/test_群二维码1个月.py \
    tests/checklist/test_群二维码永久.py \
    -v --tb=short 2>&1
  ```

- [ ] **Step 3：运行群设置/群管理相关测试（P1 集群2+3）**

  ```bash
  cd E:\UIAutotest && python -m pytest \
    tests/checklist/test_入群验证默认状态.py \
    tests/checklist/test_添加成员入口可见.py \
    tests/checklist/test_自动翻译默认状态.py \
    tests/checklist/test_添加成员点击.py \
    "tests/add/test_仅群主可编辑信息_开关.py" \
    "tests/checklist/test_仅群主可编辑公告_关闭.py" \
    "tests/checklist/test_仅群主可编辑公告_开启.py" \
    "tests/checklist/test_允许申请加群_开启.py" \
    tests/checklist/test_取消群管理员.py \
    tests/checklist/test_无管理员显示.py \
    tests/checklist/test_群主解散单人群.py \
    tests/checklist/test_群管理员详情页.py \
    tests/checklist/test_设置群管理员.py \
    tests/checklist/test_转让群主按键可见.py \
    tests/checklist/test_转让群主页面.py \
    -v --tb=short 2>&1
  ```

- [ ] **Step 4：运行图片编辑相关测试（P2 集群6）**

  ```bash
  cd E:\UIAutotest && python -m pytest \
    tests/session_msg/test_图片编辑_发送确认弹窗.py \
    tests/session_msg/test_图片编辑_多张图片编辑.py \
    tests/session_msg/test_图片编辑_编辑后发送.py \
    tests/session_msg/test_图片编辑_编辑后取消.py \
    tests/session_msg/test_图片编辑_编辑后弹窗.py \
    tests/session_msg/test_图片编辑_编辑后转发.py \
    tests/session_msg/test_图片编辑_编辑本地相册图片.py \
    "tests/add/test_会话透出_P2P图片消息.py" \
    "tests/add/test_会话透出_群聊图片消息.py" \
    "tests/add/test_长按图片消息编辑.py" \
    tests/checklist/test_相册选图编辑后发送.py \
    tests/checklist/test_使用工具编辑图片后发送.py \
    -v --tb=short 2>&1
  ```

- [ ] **Step 5：汇总失败用例，按归因顺序（图片质量→代码逻辑→设备状态）分析**

---

## 不在本次范围内

- `user.py` 中现有的委托方法（除 Task 2 中的 `click_group_qr_code`）无需修改
- 测试文件本身无需修改（方法签名完全向后兼容）
