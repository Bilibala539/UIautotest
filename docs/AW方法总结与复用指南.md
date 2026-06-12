# UIAutotest AW方法总结与复用指南

> **核心原则：编写新用例或新业务AW时，必须先查阅本文档，已封装的功能直接调用，避免重复实现。**

---

## 一、架构层级总览

```
PPUser (用户入口，user.py)
  ├── user.aw → AWHelper (aw_helper.py)
  │     ├── MuMuBusiness (business/mumu.py)    ← Android 端业务方法
  │     ├── CommonBusiness (business/common.py) ← 通用业务方法
  │     └── AWBase (aw_base.py)                 ← 基础操作(OCR/图像/点击/滑动)
  └── user.cli → PopoCLI (aw/popo_cli.py)       ← API 造数（仅用于 setup/teardown）
```

**UI 调用链路**：`self.userA.send_message(...)` → `PPUser.send_message()` → `self.aw.send_message()` → `MuMuBusiness.send_message()`

**造数调用链路**：`self.userA.cli.create_team_cli(...)` → `PopoCLI.create_team_cli()` → `popo-cli team_create`

---

## 二、基础AW方法 (AWBase 层)

这些方法是所有业务方法的底层支撑，在 `utils/aw/aw_base.py` 中实现。

### 2.1 截图相关

| 方法 | 签名 | 作用 |
|------|------|------|
| `take_screenshot` | `(save_path=None) → np.ndarray` | 截取当前窗口屏幕，可选保存到指定路径 |
| `screenshot_for_explore` | `(filename=None, subdir=None) → str` | 截图保存到探索输出目录 |
| `crop_element` | `(source_path, element_name, x1, y1, x2, y2) → str` | 从截图中裁切UI元素图片 |

### 2.2 点击操作

| 方法 | 签名 | 作用 |
|------|------|------|
| `tap` | `(x, y, dx=0, dy=0) → bool` | 点击指定窗口内坐标 |
| `long_press` | `(x, y, duration=1.0, dx=0, dy=0) → bool` | 长按指定坐标 |
| `long_press_text` | `(text, timeout=10, duration=1.5, region=ALL) → bool` | OCR找到文字后长按 |
| `long_press_image` | `(image, threshold=0.8, timeout=10, duration=1.0, region=ALL) → bool` | 模板匹配找到图片后长按 |

### 2.3 输入与按键

| 方法 | 签名 | 作用 |
|------|------|------|
| `input_text` | `(text) → bool` | 向当前焦点输入框输入文字 |
| `clear_input` | `() → bool` | 清空当前输入框 |
| `press_key` | `(key) → bool` | 按下指定按键 |
| `press_back` | `() → bool` | 按返回键 (Escape) |

### 2.4 OCR文字识别

| 方法 | 签名 | 作用 | 层级 |
|------|------|------|------|
| `find_text_by_ocr` | `(text, timeout=10, region=ALL, case_sensitive=False) → (x,y)\|None` | OCR找文字，返回文字中心坐标，**未找到返回None** | 🔍 判断层 |
| `text_exists` | `(text, timeout=5, region=ALL) → bool` | **断言**文字必须存在，不存在则assert失败 | ✅ 断言层 |
| `text_not_exists` | `(text, timeout=3, region=ALL) → bool` | **断言**文字必须不存在，存在则assert失败 | ✅ 断言层 |
| `click_text` | `(text, timeout=10, dx=0, dy=0, region=ALL)` | OCR找到文字后点击，找不到assert失败 | 👆 点击层 |

### 2.5 图像模板匹配

| 方法 | 签名 | 作用 | 层级 |
|------|------|------|------|
| `find_image` | `(template_name, threshold=0.8, timeout=10, region=ALL) → (x,y)\|None` | 模板匹配找图，**未找到返回None**（并截图保存日志） | 🔍 判断层 |
| `image_exists` | `(template_name, threshold=0.8, timeout=5, region=ALL) → bool` | **断言**图片必须存在，不存在则assert失败 | ✅ 断言层 |
| `click_image` | `(image, threshold=0.8, timeout=10, dx=0, dy=0, region=ALL)` | 找到图片后点击，找不到assert失败 | 👆 点击层 |

> **方法选择指南：**
> - 需要**条件判断**（if/else 分支）→ 用 `find_image()` / `find_text_by_ocr()`，它们找不到返回 `None`
> - 需要**验证断言**（这一步必须成功）→ 用 `image_exists()` / `text_exists()`，它们找不到 assert 失败
> - 需要**找到并点击**→ 用 `click_image()` / `click_text()`，它们找不到 assert 失败

### 2.6 滑动操作

| 方法 | 签名 | 作用 |
|------|------|------|
| `swipe` | `(start_x, start_y, end_x, end_y, duration=0.3) → bool` | 从起点滑动到终点 |
| `swipe_up` | `(distance=400) → bool` | 向上滑动（默认400px） |
| `swipe_down` | `(distance=400) → bool` | 向下滑动 |
| `swipe_left` | `(start_coords, distance=300) → bool` | 从指定位置向左滑动 |
| `swipe_right` | `(distance=300) → bool` | 向右滑动 |
| `scroll_up` | `(clicks=5) → bool` | 鼠标滚轮向上 |
| `scroll_down` | `(clicks=5) → bool` | 鼠标滚轮向下 |

### 2.7 工具方法

| 方法 | 签名 | 作用 |
|------|------|------|
| `random_digits` | `(length=10) → str` | 生成随机数字字符串，常用于生成消息内容 |
| `sleep` | `(seconds) → None` | 等待指定时间 |

---

## 三、通用业务方法 (CommonBusiness 层)

在 `utils/aw/business/common.py` 中，通用业务方法。

| 方法 | 作用 |
|------|------|
| `activate()` | 激活窗口并置于前台 |
| `go_to_home()` | 连续5次按返回键回到首页 |
| `go_to_contacts()` | 点击"联系人"文字进入通讯录 |
| `go_to_messages()` | 点击"消息"文字进入消息页 |
| `go_to_settings()` | 点击"设置"文字进入设置页 |

---

## 四、MuMu端业务AW方法详解 (MuMuBusiness 层)

在 `utils/aw/business/mumu.py` 中，以下是**已封装好的完整业务流程**。

### 4.1 🔐 登录 `login(uid, password)`

**完整流程：**
1. `click_image(HOME_POPO_LOGO)` — 点击MuMu桌面POPO图标启动应用
2. `image_exists(LOGIN_POPO_TEXT)` — 验证：检测到登录页面"网易POPO"文案
3. `click_text("邮箱")` — 点击邮箱Tab切换登录方式
4. `click_text("输入邮箱")` → `input_text(uid)` — 点击邮箱输入框并输入账号
5. `click_text("输入密码")` → `input_text(password)` — 点击密码输入框并输入密码
6. `click_image(LOGIN_READ_CENTER_FALSE)` — 勾选"阅读并同意"协议复选框
7. `click_image(LOGIN_ENTER)` — 点击登录按钮
8. `image_exists(MESSAGE_TAB_BLUE)` — **验证登录成功：消息Tab蓝色高亮**
9. `pop_not_allowed()` — 处理可能出现的权限弹窗

**验证的图片：** `LOGIN_POPO_TEXT`(登录页文案), `LOGIN_READ_CENTER_FALSE/TRUE`(协议勾选框), `LOGIN_ENTER`(登录按钮), `MESSAGE_TAB_BLUE`(消息Tab高亮)

**业务作用：** 测试的前置条件，几乎所有用例都需要先登录。

---

### 4.2 🚪 退登 `logout()`

**完整流程：**
1. `click_image(MESSAGE_TAB_BLUE)` — 确保在消息Tab页（蓝色高亮状态）
2. `click_image(MESSAGE_TAB_MSG_TEXT, dx=-70)` — 点击左上角"消息"文案左侧的头像区域，打开侧边栏
3. `click_text("设置", region=HALF_DOWN)` — 在侧边栏下半区点击"设置"
4. `click_image(SETTINGS_LOGOUT)` — 点击"退出登录"按钮
5. `click_image(SETTINGS_LOGOUT_CONFIRM)` — 点击退登确认弹窗的确认按钮
6. `image_exists(LOGIN_POPO_TEXT)` — **验证退登成功：回到登录页**

**验证的图片：** `MESSAGE_TAB_BLUE/GRUE`(Tab状态), `MESSAGE_TAB_MSG_TEXT`(消息文案定位), `SETTINGS_LOGOUT`(退出按钮), `SETTINGS_LOGOUT_CONFIRM`(确认按钮), `LOGIN_POPO_TEXT`(登录页)

**业务作用：** 测试的后置清理，恢复初始状态。

---

### 4.3 💬 发送消息 `send_message(recipient, message, isback=True)`

**完整流程：**
1. 判断 `recipient.isdigit()` → 区分P2P消息还是群组消息
2. `click_image(MESSAGE_TAB_SEARCH)` — 点击搜索按钮进入搜索页
3. `image_exists(SEARCH_EMPTY)` — 验证：搜索页空态图出现
4. `click_image(SELECT_SEARCH, dx=10)` — 点击搜索输入框
5. `input_text(recipient)` — 输入搜索关键词
6. `click_text("联系人"/"群组")` — 切换到对应搜索Tab
7. `click_text(recipient_email)` — 点击搜索结果（邮箱全称匹配）
8. `text_exists("发送给")` — **验证：成功进入聊天页面**
9. `click_text("发送给")` — 点击输入框
10. `input_text(message)` — 输入消息内容
11. `click_image(CHAT_SEND_BUTTON)` — 点击发送按钮
12. `image_exists(CHAT_PLUS_BUTTON)` — **验证发送成功：发送按钮恢复为"+"号**
13. 若 `isback=True`：`press_back()` → `image_exists(MESSAGE_TAB_BLUE)` — 返回消息列表并验证

**验证的图片：** `MESSAGE_TAB_SEARCH`(搜索按钮), `SEARCH_EMPTY`(空态), `SELECT_SEARCH`(搜索框), `CHAT_SEND_BUTTON`(发送按钮), `CHAT_PLUS_BUTTON`(加号按钮), `MESSAGE_TAB_BLUE`(消息Tab)

**业务作用：** ⭐ **高频复用方法**。发送消息是许多测试场景的前置条件，如：撤回消息、转发消息、回复消息、消息已读等。

---

### 4.4（内部实现）`_longpress_and_select_menu_item(message_text, menu_item)`

> **私有 helper，外部用例请勿直接调用。**

所有简单长按菜单操作的公共 3 步样板：
1. `long_press_text(message_text, duration=1.5)` — 长按消息气泡（1.5秒）
2. `click_text(menu_item, region=HALF_DOWN)` — 点击弹出菜单中的指定项
3. 各 sleep 保证 UI 响应（长按后 1s、点击后 1s）

**使用此 helper 的方法：** `recall_message` / `copy_message` / `multi_select_message` / `translate_message` / `delete_message` / `pin_message`

**未使用此 helper 的方法：** `reply_message`（需额外输入+发送步骤）、`favorite_message`（有重试循环+复杂检测逻辑）

---

### 4.4 🔄 撤回消息 `recall_message(message_text)`

**前置条件：** 当前在聊天页面，消息为自己发送且24小时内。

**完整流程：**
1. `find_text_by_ocr(message_text)` — 获取消息 y 坐标（用于后续验证范围）
2. `_longpress_and_select_menu_item(message_text, "撤回")` — 长按并从菜单点击"撤回"
3. `find_image(MSG_RECELL_POP)` → 若有确认弹窗则 `click_text("确定")`
4. `text_exists("你撤回了一条消息", region=(msg_y±60px))` — **验证撤回成功**

**验证的图片：** `MSG_RECELL_POP`(撤回确认弹窗)

**业务作用：** 消息撤回功能验证。注意该方法需要当前页面已在聊天页内，通常与 `send_message(isback=False)` 配合使用。

---

### 4.4a 💬 回复消息 `reply_message(message_text, reply_content)`

**前置条件：** 当前在聊天页面。

**完整流程：**
1. `long_press_text(message_text, duration=1.5)` — 长按目标消息
2. `click_text("回复", region=HALF_DOWN)` — 点击弹出菜单中的"回复"
3. `image_exists(CHAT_REPLY_QUOTE_BAR, region=HALF_DOWN)` — **验证：引用栏出现**
4. `input_text(reply_content)` — 输入回复内容
5. `click_image(CHAT_SEND_BUTTON, region=HALF_DOWN)` — 点击发送
6. `image_exists(CHAT_PLUS_BUTTON, region=HALF_DOWN)` — **验证：发送成功**

**验证的图片：** `CHAT_REPLY_QUOTE_BAR`(引用栏), `CHAT_SEND_BUTTON`(发送按钮), `CHAT_PLUS_BUTTON`(+号恢复)

**业务作用：** 消息回复功能，引用原消息并发送回复内容。

---

### 4.4b 📋 复制消息 `copy_message(message_text)`

**前置条件：** 当前在聊天页面。

**完整流程：**
1. `_longpress_and_select_menu_item(message_text, "复制")` — 长按并从菜单点击"复制"
2. `image_exists(CHAT_COPY_SUCCESS_TOAST)` — **验证：复制成功toast**

**验证的图片：** `CHAT_COPY_SUCCESS_TOAST`(复制成功提示)

**业务作用：** 复制消息文字内容到系统剪贴板。

---

### 4.4c ☑️ 多选消息 `multi_select_message(message_text)`

**前置条件：** 当前在聊天页面。

**完整流程：**
1. `_longpress_and_select_menu_item(message_text, "多选")` — 长按并从菜单点击"多选"
2. `image_exists(CHAT_MULTI_SELECT_TITLE, region=HALF_UP)` — **验证：进入多选模式**
3. `press_back()` — 退出多选模式

**验证的图片：** `CHAT_MULTI_SELECT_TITLE`(多选模式标题栏"已选中")

**业务作用：** 进入多选模式并退出，验证多选功能可用。

---

### 4.4d 🌐 翻译消息 `translate_message(message_text)`

**前置条件：** 当前在聊天页面。

**完整流程：**
1. `find_text_by_ocr(message_text)` — 获取消息 y 坐标（用于后续验证范围）
2. `_longpress_and_select_menu_item(message_text, "翻译")` — 长按并从菜单点击"翻译"
3. `image_exists(CHAT_TRANSLATE_RESULT, region=(msg_y±100px))` — **验证：翻译结果出现（scoped）**

**验证的图片：** `CHAT_TRANSLATE_RESULT`(翻译结果区域)

**业务作用：** 翻译消息文字，翻译结果显示在气泡下方。

---

### 4.4e ⭐ 收藏消息 `favorite_message(message_text)`

**前置条件：** 当前在聊天页面。

**完整流程：**
1. `long_press_text(message_text, duration=1.5)` — 长按目标消息
2. `click_text("收藏", region=HALF_DOWN)` — 点击弹出菜单中的"收藏"
3. `image_exists(CHAT_FAVORITE_TOAST)` — **验证：已收藏toast**

**验证的图片：** `CHAT_FAVORITE_TOAST`(已收藏提示)

**业务作用：** 收藏消息到"我的收藏"。

---

### 4.5 👥 创建群组 `create_team()`

**完整流程：**
1. `click_image(SESSIONLIST_PLUS_BUTTON)` — 点击会话列表右上角"+"按钮
2. `click_image(SESSIONLIST_PLUS_BUTTON_CREATETEAM)` — 点击"创建群聊"选项
3. `image_exists(SELECT_TITLE_ADD_TEAM_MUNBER)` — 验证：进入"添加群成员"页
4. `click_image(SELECT_SEARCH)` → `input_text("grp.popoqa")` — 搜索群成员
5. `click_image(SELECT_CIRCLE)` — 选中搜索结果（点击圆形勾选框）
6. `image_exists(SELECT_CIRCLE_BLUE)` — 验证：勾选框变为蓝色
7. `click_image(SELECT_OK_BLUE)` — 点击确认按钮
8. 可能出现"选择已有群组"弹窗 → `click_image(CREATE_NEW_TEAM)` 选择创建新群
9. `text_exists("发起群聊"/"并邀请"/"加入群聊")` — **验证创建成功**

**验证的图片：** `SESSIONLIST_PLUS_BUTTON`(+按钮), `SESSIONLIST_PLUS_BUTTON_CREATETEAM`(创建群聊), `SELECT_TITLE_ADD_TEAM_MUNBER`(添加成员标题), `SELECT_SEARCH`(搜索框), `SELECT_CIRCLE`/`SELECT_CIRCLE_BLUE`(勾选框), `SELECT_OK_BLUE`(确认按钮), `CREATE_NEW_TEAM`(创建新群组)

**业务作用：** 创建群聊，是群组相关测试的前置条件。

---

### 4.6 📋 侧边栏操作

#### `open_sidebar()`
1. `click_image(MESSAGE_TAB_MSG_TEXT, dx=-70)` — 点击"消息"文案左侧约70px处（头像区域）
2. `image_exists(SIDEBAR_SETTINGS_BUTTON)` — **验证：侧边栏打开成功**（设置按钮可见）

#### `close_sidebar()`
1. `press_back()` — 按返回键关闭侧边栏

**业务作用：** 打开侧边栏是进入设置、我的收藏、个人资料等功能的入口。

---

### 4.7 👤 查看个人资料 `view_my_profile() → dict`

**完整流程：**
1. `open_sidebar()` — 打开侧边栏
2. `image_exists(SIDEBAR_MY_COLLECTION)` → `click_image(SIDEBAR_MY_COLLECTION, dy=-180)` — 点击"我的收藏"上方180px处（用户名区域）
3. `find_text_by_ocr("个性签名")` / `find_text_by_ocr("中文昵称")` — 验证进入个人资料页
4. `_extract_profile_fields()` — 逐字段OCR采集：个性签名、中文昵称、英文昵称、日文昵称、账号、手机号
5. `swipe_up(300)` — 向上滑动查看更多信息
6. 继续采集：岗位名称、组织架构、办公位置
7. 两次 `press_back()` — 返回消息列表

**业务作用：** 个人资料展示验证，采集各字段确认数据正确性。

---

### 4.8 ⭐ 打开我的收藏 `open_my_collection()`
1. `open_sidebar()` — 打开侧边栏
2. `click_image(SIDEBAR_MY_COLLECTION)` — 点击"我的收藏"

### 4.9 📱 打开登录设备管理 `open_device_management()`
1. `open_sidebar()` — 打开侧边栏
2. `click_image(SIDEBAR_DEVICE_MANAGEMENT)` — 点击"登录设备管理"

### 4.10 ⚙️ 打开设置 `open_settings()`
1. `open_sidebar()` — 打开侧边栏
2. `click_image(SIDEBAR_SETTINGS_BUTTON)` — 点击"设置"按钮

---

### 4.11 🔍 大搜功能 `search(tab, text, isclose=True)`

**完整流程：**
1. `click_image(MESSAGE_TAB_SEARCH)` — 从消息页点击搜索按钮
2. `image_exists(SEARCH_EMPTY)` — 验证：搜索空态页出现
3. 若 tab 在 ["云空间","任务","应用"]：向左滑动翻页露出对应Tab
4. 若 tab ≠ "全部"：`click_image(搜索页面-{tab}tab-未选中.png)` — 切换到对应Tab
5. `image_exists(搜索页面-{tab}tab.png)` — 验证：Tab已选中
6. `click_image(SELECT_SEARCH, dx=10)` → `input_text(text)` — 输入搜索关键词
7. 若 `isclose=True`：`click_image(SEARCH_CANCEL)` — 退出搜索页

**业务作用：** ⭐ **高频复用方法**。搜索是进入各种功能页面的通用入口。

---

### 4.11b 🖼️ 图片编辑相关

#### `send_image_from_album(recipient)` — 从相册选图并直接发送

**前置条件：** 消息Tab页面
**完整流程：**
1. `_enter_chat_page(recipient)` — 搜索进入聊天页
2. `click_image(CHAT_PLUS_BUTTON)` — 打开+面板
3. `click_image(CHAT_PLUS_ALBUM)` — 点击相册
4. `tap(70, 200)` — 点击第一张图片
5. `click_text("发送")` — 点击发送
6. `image_exists(CHAT_PLUS_BUTTON)` — **验证发送成功**

**业务作用：** 图片发送前置条件，为长按图片测试用例提供图片消息。

---

#### `select_edit_send_image_from_album(recipient)` — 相册选图→编辑→发送

**完整流程：**
1. `_enter_chat_page(recipient)` → `click_image(CHAT_PLUS_BUTTON)` → `click_image(CHAT_PLUS_ALBUM)` — 进入相册
2. `tap(70, 200)` — 选择第一张图片
3. `click_text("预览")` — 进入全屏预览模式
4. `click_image(ALBUM_PREVIEW_EDIT_BUTTON)` — 点击"编辑"按钮进入编辑器
5. `image_exists(IMAGE_EDITOR_TOOLBAR)` — **验证：编辑器工具栏出现**
6. `click_image(IMAGE_EDITOR_DONE_BUTTON)` — 点击"完成"退出编辑器
7. `image_exists(ALBUM_PREVIEW_EDIT_BUTTON)` — **验证：返回预览页**
8. `click_image(ALBUM_PREVIEW_SEND_BUTTON)` — 点击"发送"
9. `image_exists(CHAT_PLUS_BUTTON)` — **验证：发送成功**

**验证图片：** `ALBUM_PREVIEW_EDIT_BUTTON`, `IMAGE_EDITOR_TOOLBAR`, `IMAGE_EDITOR_DONE_BUTTON`, `ALBUM_PREVIEW_SEND_BUTTON`

---

#### `edit_image_from_chat_message()` — 长按图片消息→编辑图片

**前置条件：** 当前在聊天页，聊天中已有图片消息。
**完整流程：**
1. `long_press_image(CHAT_SENT_IMAGE_BUBBLE, duration=1.5)` — 长按图片气泡
2. `click_text("编辑图片", region=Normal.HALF_DOWN)` — OCR点击"编辑图片"（长按菜单文字选项）
3. `image_exists(IMAGE_EDITOR_TOOLBAR)` — **验证：进入编辑器**
4. `click_image(IMAGE_EDITOR_DONE_BUTTON)` — 完成编辑
5. `image_exists(CHAT_PLUS_BUTTON)` — **验证：返回聊天页**

---

#### `select_edit_with_tools_send_image(recipient)` — 相册选图→工具编辑→发送

与 `select_edit_send_image_from_album` 类似，但额外在编辑器中执行 `swipe(150,400,380,400)` 使用画笔工具绘制。

---

### 4.11c 🔙 返回消息列表页 `return_to_message_list(max_back=6, strict=False)`

**作用：** 从任意深度页面（聊天页、群设置、标签页管理等）连续按返回键，直到检测到消息列表页（`MESSAGE_TAB_BLUE`）为止。这是全工程唯一的「返回消息列表」实现，任何新 AW 方法均应调用此方法，**不要再写内联 for 循环**。

**参数：**

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `max_back` | int | 6 | 最多按几次返回键（深层页面可传更大值，如 8） |
| `strict` | bool | False | `False` = 失败只记 warning；`True` = 失败直接 assert（适用于关键流程） |

**典型用法：**

```python
# AW 层——普通用法，任意深度返回，失败只 warning
self.return_to_message_list()

# AW 层——严格模式，send_message 等关键流程，返回失败即报错
self.return_to_message_list(max_back=5, strict=True)

# AW 层——深层页面（群设置、搜索历史等 8 层）
self.return_to_message_list(max_back=8)

# PPUser 层——用例中直接调用
self.userA.return_to_message_list()
self.userA.return_to_message_list(max_back=8, strict=True)
```

---

### 4.12 应用控制
|------|------|
| `start_app()` | 点击桌面POPO图标启动应用 |
| `stop_app()` | ADB强制停止应用 |
| `restart_app()` | 先stop再start |
| `clear_app_data()` | ADB清除应用数据 |

### 4.13 弹窗处理

| 方法 | 作用 |
|------|------|
| `pop_not_allowed()` | 检测弹窗并点击取消 |
| `pop_allowed()` | 检测弹窗并允许 |
| `pop_is_exisit(isallow)` | 通用弹窗检测，验证图片`POPO_POP`，取消用`POPO_POP_CANCEL` |

---

## 五、PPUser 便捷方法（用户层封装）

在 `utils/user.py` 中，PPUser 将业务方法进一步封装为用户级接口。

### 5.1 已封装的业务快捷方法

| PPUser方法 | 调用的底层方法 | 说明 |
|-----------|--------------|------|
| `user.login()` | `aw.login(uid, password)` | 登录 |
| `user.logout()` | `aw.logout()` | 退登 |
| `user.send_message(recipient, message, isback)` | `aw.send_message(...)` | ⭐ 发消息(搜人+进会话+发送) |
| `user.recall_message(message_text)` | `aw.recall_message(...)` | 撤回消息 |
| `user.reply_message(message_text, reply_content)` | `aw.reply_message(...)` | 回复消息（引用回复） |
| `user.copy_message(message_text)` | `aw.copy_message(...)` | 复制消息 |
| `user.multi_select_message(message_text)` | `aw.multi_select_message(...)` | 多选消息 |
| `user.translate_message(message_text)` | `aw.translate_message(...)` | 翻译消息 |
| `user.favorite_message(message_text)` | `aw.favorite_message(...)` | 收藏消息 |
| `user.create_team()` | `aw.create_team()` | 创建群组 |
| `user.delete_team()` | `aw.delete_team()` | 解散群组(未实现) |
| `user.open_sidebar()` | `aw.open_sidebar()` | 打开侧边栏 |
| `user.view_my_profile()` | `aw.view_my_profile()` | 查看个人资料 |
| `user.open_my_collection()` | `aw.open_my_collection()` | 打开我的收藏 |
| `user.open_settings()` | `aw.open_settings()` | 打开设置 |
| `user.search(tab, text, isclose)` | `aw.search(...)` | ⭐ 大搜功能 |
| `user.search_people(text)` | 搜联系人 | 搜人并验证结果 |
| `user.search_group(text)` | 搜群 | 搜群并验证结果 |
| `user.search_msg(tab, text)` | 搜消息 | 搜消息并验证结果 |
| `user.send_image_from_album(recipient)` | `aw.send_image_from_album(...)` | 从相册选图直接发送（不编辑） |
| `user.return_to_message_list(max_back, strict)` | `aw.return_to_message_list(...)` | 🔙 从任意深度返回消息列表页 |
| `user.select_edit_send_image_from_album(recipient)` | `aw.select_edit_send_image_from_album(...)` | 相册选图→预览→编辑→完成→发送 |
| `user.edit_image_from_chat_message()` | `aw.edit_image_from_chat_message()` | 长按图片消息→编辑图片→完成 |
| `user.select_edit_with_tools_send_image(recipient)` | `aw.select_edit_with_tools_send_image(...)` | 相册选图→工具编辑→发送 |

### 5.2 已封装的基础操作快捷方法

| PPUser方法 | 说明 |
|-----------|------|
| `user.click_image(image_name, ...)` | 点击图片 |
| `user.image_exists(template_name, ...)` | 断言图片存在 |
| `user.click_text(text, ...)` | 点击文字 |
| `user.text_exists(text, ...)` | 断言文字存在 |
| `user.text_not_exists(text, ...)` | 断言文字不存在 |
| `user.input_text(text)` | 输入文本 |
| `user.tap(x, y, ...)` | 点击坐标 |
| `user.wait_and_click_text(text, timeout)` | 等待文字出现再点击 |
| `user.wait_and_click_image(image_name, timeout)` | 等待图片出现再点击 |

---

## 六、CLI 造数方法 (PopoCLI)

> **⚠️ 仅用于造数，不做 UI 验证。**
> 这些方法通过 `popo-cli` API 直接操作数据，速度快（1-2s）、无副作用，
> 适合在 `setup()` / `teardown()` 中准备或清理测试前置数据。
> **不要在测试步骤中调用，UI 验证必须走 `user.aw` 方法。**

通过 `self.userA.cli` 访问，uid 自动绑定为当前用户，无需手动传入。  
源文件：`utils/aw/popo_cli.py`

---

### 6.1 群组管理

#### `create_team_cli(uid_list, name=None) → (tid, name)`

创建群组，当前用户自动成为群主并入群。

| 参数 | 类型 | 说明 |
|------|------|------|
| `uid_list` | `list[str]` | 被邀请成员的 uid 列表（不含当前用户自身） |
| `name` | `str\|None` | 群名，不传则系统自动生成 |

**返回：** `(tid: str, name: str)`

```python
tid, name = self.userA.cli.create_team_cli(
    name="消息透出测试群",
    uid_list=["grp.popoqa67@corp.netease.com"],
)
```

---

#### `invite_member_cli(tid, uid_list, name=None) → dict`

邀请成员加入已有群组。

| 参数 | 类型 | 说明 |
|------|------|------|
| `tid` | `str` | 群 ID |
| `uid_list` | `list[str]` | 被邀请成员的 uid 列表 |
| `name` | `str\|None` | 群名（可选，仅用于标注，不影响操作） |

**返回：** `{"tid": str, "name": str, "pass_num": int}`  
注：群成员列表/总人数 popo-cli 无对应接口，不在返回值中。

```python
result = self.userA.cli.invite_member_cli(
    tid=tid,
    uid_list=["grp.popoqa73@corp.netease.com"],
    name="测试群",
)
# result["pass_num"] == 1
```

---

#### `kick_member_cli(tid, uid_list, name=None) → dict`

从群组移除成员，自动反查被移除人的姓名。

| 参数 | 类型 | 说明 |
|------|------|------|
| `tid` | `str` | 群 ID |
| `uid_list` | `list[str]` | 被移除成员的 uid 列表 |
| `name` | `str\|None` | 群名（可选） |

**返回：** `{"tid": str, "name": str, "kicked_uids": list, "kicked_names": list}`  
注：剩余成员列表/人数 popo-cli 无对应接口，不在返回值中。

```python
result = self.userA.cli.kick_member_cli(
    tid=tid,
    uid_list=["grp.popoqa73@corp.netease.com"],
    name="测试群",
)
# result["kicked_names"] == ["grp73"]
```

---

#### `update_team_name_cli(tid, name) → dict`

修改群名。

**返回：** `{"tid": str, "name": str}`

```python
result = self.userA.cli.update_team_name_cli(tid=tid, name="新群名")
```

---

### 6.2 消息发送（文本 / 图片 / 文件）

`send_message_p2p_cli` 和 `send_message_team_cli` 支持三种消息类型，**三选一传参**。

| 消息类型 | 传参 | 返回值 |
|---------|------|--------|
| 文本 | `message="内容"` | `str` — 消息内容 |
| 图片 | `image_path="E:/xx.png"` | `str` — 图片本地路径 |
| 文件 | `file_path="E:/xx.pdf"` | `(filename: str, file_path: str)` |

#### `send_message_p2p_cli(receiver, *, message, image_path, file_path)`

向指定用户发送 P2P 消息。

```python
# 文本
msg = self.userA.cli.send_message_p2p_cli(
    receiver="grp.popoqa67@corp.netease.com", message="测试消息"
)
# msg == "测试消息"

# 图片
path = self.userA.cli.send_message_p2p_cli(
    receiver="grp.popoqa67@corp.netease.com", image_path="E:/shot.png"
)

# 文件
fname, fpath = self.userA.cli.send_message_p2p_cli(
    receiver="grp.popoqa67@corp.netease.com", file_path="E:/report.pdf"
)
```

#### `send_message_team_cli(tid, *, message, image_path, file_path)`

向群组发送消息，`tid` 替换 `receiver`，其余同上。

```python
msg = self.userA.cli.send_message_team_cli(tid="8479417", message="群消息")

fname, fpath = self.userA.cli.send_message_team_cli(
    tid="8479417", file_path="E:/attach.zip"
)
```

---

### 6.3 日历

#### `create_schedule_cli(title, start_time, end_time, participants=None, location=None, content=None) → dict`

创建日程/会议，自动发送邀请通知。

| 参数 | 类型 | 说明 |
|------|------|------|
| `title` | `str` | 会议标题 |
| `start_time` | `str` | 开始时间（ISO-8601，含时区，如 `2026-06-10T14:00:00+08:00`） |
| `end_time` | `str` | 结束时间（ISO-8601） |
| `participants` | `list[str]\|None` | 参与人 uid 列表 |
| `location` | `str\|None` | 地点 |
| `content` | `str\|None` | 备注 |

**返回：** `{"schedule_id": int, "title": str, "participants": list[str]}`

```python
info = self.userA.cli.create_schedule_cli(
    title="项目评审",
    start_time="2026-06-10T14:00:00+08:00",
    end_time="2026-06-10T15:00:00+08:00",
    participants=["grp.popoqa67@corp.netease.com"],
)
schedule_id = info["schedule_id"]
```

---

#### `update_schedule_cli(schedule_id, title=None, start_time=None, end_time=None, add_participants=None, remove_participants=None, location=None, content=None) → dict`

修改日程，操作后自动查询并返回修改后的完整信息。

**返回：** `{"schedule_id": int, "title": str, "start_time": str, "end_time": str, "participants": list[{"uid", "name"}]}`

```python
info = self.userA.cli.update_schedule_cli(
    schedule_id=schedule_id,
    title="新会议名",
    end_time="2026-06-10T16:00:00+08:00",
    add_participants=["grp.popoqa73@corp.netease.com"],
)
```

---

#### `confirm_schedule_cli(schedule_id, status) → dict`

接受或拒绝日程邀请，操作前自动查询日程信息。

| 参数 | 类型 | 说明 |
|------|------|------|
| `schedule_id` | `int` | 日程 ID |
| `status` | `int` | `1`=接受，`2`=拒绝 |

**返回：** `{"schedule_id": int, "title": str, "participants": list[{"uid", "name"}]}`

```python
info = self.userA.cli.confirm_schedule_cli(schedule_id=schedule_id, status=1)
```

---

#### `quit_schedule_cli(schedule_id) → dict`

退出日程（参与人主动退出），操作前自动查询日程名称。

**返回：** `{"schedule_id": int, "title": str}`

```python
info = self.userA.cli.quit_schedule_cli(schedule_id=schedule_id)
```

---

### 6.4 完整造数示例

```python
class TestGroupMemberManage(BaseTest):
    def setup(self):
        self.userA = self.users("userA")
        # 造数：创建测试群并邀请成员
        self.tid, self.gname = self.userA.cli.create_team_cli(
            name="成员管理测试群",
            uid_list=["grp.popoqa67@corp.netease.com"],
        )
        inv = self.userA.cli.invite_member_cli(
            tid=self.tid,
            uid_list=["grp.popoqa73@corp.netease.com"],
            name=self.gname,
        )
        assert inv["pass_num"] == 1

    def test_kick_member(self):
        # UI 操作：在群管理页移除成员，验证 UI 反馈
        self.userA.aw.enter_group_management(self.gname)
        # ... UI 验证 ...

    def teardown(self):
        # 造数清理：用 CLI 快速移除成员，无需走 UI
        self.userA.cli.kick_member_cli(
            tid=self.tid,
            uid_list=["grp.popoqa73@corp.netease.com"],
        )
```

---

### 6.5 造数 vs UI 操作对比

| 场景 | 用造数 CLI | 用 UI 方法 |
|------|-----------|-----------|
| setup 中需要一个测试群 | ✅ `cli.create_team_cli(...)` — ~1s | ❌ UI 建群 10s+，受 App 状态影响 |
| setup 中需要给群加成员 | ✅ `cli.invite_member_cli(...)` | ❌ 需走完整 UI 邀请流程 |
| teardown 中清理群成员 | ✅ `cli.kick_member_cli(...)` | ❌ 需走完整 UI 移除流程 |
| setup 中需要对端先发消息 | ✅ `cli.send_message_p2p_cli(...)` | ❌ 需要启动第二个模拟器 |
| setup 中需要发图片/文件给对端 | ✅ `cli.send_message_p2p_cli(image_path=...)` | ❌ 需要模拟器相册/文件 |
| setup 中需要创建会议并邀请参与人 | ✅ `cli.create_schedule_cli(...)` | ❌ 日历功能无 UI 封装 |
| 测试"发消息"功能本身 | ❌ 不适用 | ✅ `user.send_message(...)` |
| 验证消息/群成员是否正确展示 | ❌ 不适用 | ✅ `user.aw.text_exists(...)` 等 |

---

## 七、复用指南 — 编写新用例时的正确姿势

### ✅ 正确做法：调用已封装的业务方法

```python
# 场景：撤回一条P2P消息
class TestRecallMessage(BaseTest):
    def setup(self):
        self.userA = self.users("userA")
        self.userA.login()

    def test_recall_p2p_message(self):
        # ✅ 直接调用send_message，它会自动完成：搜人→进会话→输入→发送→验证
        message = self.userA.send_message(recipient="grp.popoqa93", isback=False)
        # ✅ 直接调用recall_message，它会自动完成：长按→点撤回→确认→验证
        self.userA.recall_message(message)
        self.userA.aw.press_back()

    def teardown(self):
        self.userA.logout()
```

### ❌ 错误做法：重复实现已有逻辑

```python
# ❌ 不要这样写！send_message 已经封装了全部流程
def test_recall_p2p_message(self):
    # 不需要手动一步一步搜人、进会话、输入、发送
    self.userA.click_image(MESSAGE_TAB_SEARCH)
    self.userA.click_image(SELECT_SEARCH)
    self.userA.input_text("grp.popoqa93")
    self.userA.click_text("联系人")
    self.userA.click_text("grp.popoqa93@corp.netease.com")
    # ... 这些全部已经在 send_message 中封装好了！
```

### 📋 常见场景对应的复用方法

| 测试场景 | 推荐复用的方法 | 说明 |
|---------|--------------|------|
| 需要先发一条消息 | `user.send_message(recipient, message, isback=False)` | isback=False 留在聊天页，方便后续操作 |
| 需要先进入某人会话 | `user.send_message(recipient, message, isback=False)` | 发消息过程中会自动进入会话 |
| 需要先搜索某内容 | `user.search(tab, text, isclose=False)` | isclose=False 留在搜索结果页 |
| 需要先打开侧边栏 | `user.open_sidebar()` | 已封装进入侧边栏的完整流程 |
| 需要先进入设置页 | `user.open_settings()` | 已封装：侧边栏→设置 |
| 需要登录/退登 | `user.login()` / `user.logout()` | 标准setup/teardown |
| 需要创建群聊（UI验证建群功能） | `user.create_team()` | 完整的建群 UI 流程 |
| **需要创建群聊（作为前置数据）** | `user.cli.create_team_cli(name, uid_list)` | ⚡ CLI 造数，~1s，返回 `(tid, name)` |
| **需要给已有群邀请成员（前置数据）** | `user.cli.invite_member_cli(tid, uid_list)` | ⚡ CLI 造数，返回 `{"tid", "pass_num"}` |
| **需要移除群成员（teardown 清理）** | `user.cli.kick_member_cli(tid, uid_list)` | ⚡ CLI 造数，返回 `{"kicked_names"}` |
| **需要修改群名（前置数据）** | `user.cli.update_team_name_cli(tid, name)` | ⚡ CLI 造数，返回 `{"tid", "name"}` |
| **需要对端发文本消息（前置数据）** | `user.cli.send_message_p2p_cli(receiver, message=...)` | ⚡ CLI 造数，返回消息内容字符串 |
| **需要对端发图片消息（前置数据）** | `user.cli.send_message_p2p_cli(receiver, image_path=...)` | ⚡ CLI 造数，返回图片路径 |
| **需要对端发文件消息（前置数据）** | `user.cli.send_message_p2p_cli(receiver, file_path=...)` | ⚡ CLI 造数，返回 `(filename, path)` |
| **需要群里有一条消息（前置数据）** | `user.cli.send_message_team_cli(tid, message=...)` | ⚡ CLI 造数，返回消息内容字符串 |
| **需要创建会议/日程（前置数据）** | `user.cli.create_schedule_cli(title, start, end, participants=...)` | ⚡ CLI 造数，返回 `{"schedule_id", "title"}` |
| **需要修改日程（前置数据）** | `user.cli.update_schedule_cli(schedule_id, ...)` | ⚡ CLI 造数，返回修改后的完整信息 |
| **需要接受/拒绝日程邀请** | `user.cli.confirm_schedule_cli(schedule_id, status=1)` | ⚡ CLI 造数，返回 `{"title", "participants"}` |
| **需要退出日程（teardown 清理）** | `user.cli.quit_schedule_cli(schedule_id)` | ⚡ CLI 造数，返回 `{"title"}` |
| 需要查看个人资料 | `user.view_my_profile()` | 返回资料字典 |

---

## 八、图片常量索引

所有图片常量定义在 `image/image_name_mapping.py` 中。

### 正式图片 (image/ 目录) — 已验证通过

| 分类 | 常量名 | 文件名 | 用途 |
|------|--------|--------|------|
| **登录页** | `LOGIN_POPO_TEXT` | 登录页-网易popo文案.png | 判断是否在登录页 |
| | `HOME_POPO_LOGO` | 桌面-logo.png | 桌面POPO图标 |
| | `LOGIN_READ_CENTER_FALSE` | 登录页-阅读同意勾选框-未勾选.png | 协议勾选(未勾) |
| | `LOGIN_READ_CENTER_TRUE` | 登录页-阅读同意勾选框-已勾选.png | 协议勾选(已勾) |
| | `LOGIN_ENTER` | 登录页-登录按钮.png | 登录按钮 |
| **消息Tab** | `MESSAGE_TAB_BLUE` | 消息tab页-导航栏消息蓝色高亮.png | 消息Tab选中状态 |
| | `MESSAGE_TAB_GRUE` | 消息tab页-导航栏消息灰色.png | 消息Tab未选中状态 |
| | `MESSAGE_TAB_MSG_TEXT` | 消息tab页-左上角消息文案.png | 左上角"消息"文字 |
| | `MESSAGE_TAB_SEARCH` | 会话列表页-搜索按钮.png | 搜索入口 |
| **侧边栏** | `SIDEBAR_MY_COLLECTION` | 侧边栏-我的收藏.png | 我的收藏 |
| | `SIDEBAR_DEVICE_MANAGEMENT` | 侧边栏-登录设备管理.png | 设备管理 |
| | `SIDEBAR_SETTINGS_BUTTON` | 侧边栏-设置按钮.png | 设置按钮 |
| **设置页** | `SETTINGS_LOGOUT` | 设置页-退出登录.png | 退登按钮 |
| | `SETTINGS_LOGOUT_CONFIRM` | 退登确认弹窗-退出登录.png | 退登确认 |
| **聊天页** | `CHAT_SEND_BUTTON` | 聊天页-发送按钮.png | 发送按钮 |
| | `CHAT_PLUS_BUTTON` | 聊天页-更多加号按钮.png | +号按钮(发送成功标志) |
| | `MSG_RECELL_POP` | 撤回消息确认弹窗.png | 撤回确认弹窗 |
| | `CHAT_REPLY_QUOTE_BAR` | 聊天页-回复引用蓝线.png | 回复引用栏蓝色竖线(已转正) |
| | `CHAT_REPLY_QUOTE_CLOSE` | 聊天页-回复引用关闭按钮.png | 引用关闭按钮(已转正) |
| | `CHAT_COPY_SUCCESS_TOAST` | 聊天页-复制成功toast.png | 复制成功提示(已转正) |
| | `CHAT_MULTI_SELECT_TITLE` | 聊天页-多选模式标题.png | 多选模式标题(已转正) |
| | `CHAT_TRANSLATE_RESULT` | 聊天页-翻译结果.png | 翻译结果区域(已转正) |
| | `CHAT_FAVORITE_TOAST` | 聊天页-已收藏toast.png | 已收藏提示(已转正) |
| **搜索页** | `SEARCH_EMPTY` | 搜索页面-空态图片.png | 搜索空态 |
| | `SEARCH_CANCEL` | 搜索页面-输入框右侧取消.png | 取消搜索 |
| | `SELECT_SEARCH` | 选人组件-搜索框.png | 搜索输入框 |
| **选人组件** | `SELECT_CIRCLE` / `SELECT_CIRCLE_BLUE` | 选人组件-圆形勾选框.png | 选人勾选 |
| | `SELECT_OK_BLUE` | 选人组件-确认按钮蓝色.png | 选人确认 |
| **弹窗** | `POPO_POP` | 中心弹窗-悬浮窗权限弹窗.png | 权限弹窗 |
| | `POPO_POP_CANCEL` | 中心弹窗-悬浮窗权限弹窗-取消按钮.png | 弹窗取消 |

### 草稿图片 (image_ai/ 目录) — 待验证

| 分类 | 常量名 | 文件名 | 用途 |
|------|--------|--------|------|
| **群设置页** | `GROUP_SETTINGS_*` | 群设置页-*.png | 群设置相关元素 |
| **通讯录页** | `CONTACTS_*` | 通讯录页-*.png | 通讯录相关元素 |

### 已转正图片 (image/ 目录) — 图片编辑功能

| 分类 | 常量名 | 文件名 | 用途 |
|------|--------|--------|------|
| **图片编辑** | `CHAT_PLUS_ALBUM` | 聊天页-更多加号-相册.png | +面板中的相册入口 |
| | `CHAT_SENT_IMAGE_BUBBLE` | 聊天页-已发送图片气泡.png | 已发送图片消息气泡（用于长按）|
| | `ALBUM_PREVIEW_EDIT_BUTTON` | 相册预览页-编辑按钮.png | 预览页"编辑"按钮 |
| | `ALBUM_PREVIEW_SEND_BUTTON` | 相册预览页-发送按钮.png | 预览页"发送"按钮 |
| | `IMAGE_EDITOR_DONE_BUTTON` | 图片编辑器-完成按钮.png | 编辑器"完成"按钮 |
| | `IMAGE_EDITOR_TOOLBAR` | 图片编辑器-底部工具栏.png | 编辑器底部工具栏（页面识别用） |

---

## 九、搜索区域常量 (search_region.py)

| 常量 | 值 (x, y, w, h) | 含义 |
|------|-----------------|------|
| `Normal.ALL` | (0, 0, 540, 960) | 全屏 |
| `Normal.HALF_UP` | (0, 0, 540, 480) | 上半屏 |
| `Normal.HALF_DOWN` | (0, 480, 540, 480) | 下半屏 |
| `Normal.HALF_LEFT` | (0, 0, 270, 960) | 左半屏 |
| `Normal.HALF_RIGHT` | (270, 0, 270, 960) | 右半屏 |
| `Normal.CENTER_POP` | (0, 240, 540, 720) | 中间区域 |
| `Search.RESULT_LIST` | (0, 198, 540, 960) | 搜索结果列表区域 |

---

## 十、尚未实现的功能（需要新建AW）

- `delete_team()` — 解散群组（方法存在但为空实现）
- 转发消息
- ~~回复消息~~ ✅ 已实现 → `reply_message(message_text, reply_content)`
- @某人
- ~~复制消息~~ ✅ 已实现 → `copy_message(message_text)`
- ~~收藏消息~~ ✅ 已实现 → `favorite_message(message_text)`
- 多选消息后的批量操作（转发/删除等，当前仅验证进入多选模式）
- 翻译消息后的收起/展开操作（当前仅验证翻译结果出现）
- 消息已读/未读状态检查
- 群组管理（修改群名、添加/移除成员）
- ~~从相册选图编辑后发送~~ ✅ 已实现 → `select_edit_send_image_from_album(recipient)`
- ~~长按图片消息并编辑~~ ✅ 已实现 → `edit_image_from_chat_message()`
- ~~使用工具编辑图片后发送~~ ✅ 已实现 → `select_edit_with_tools_send_image(recipient)`
- 通讯录页面的完整操作

---

> **总结核心要点：** 在编写任何新的测试用例或业务AW时，首先检查本文档中是否已有可复用的方法。特别是 `send_message`、`search`、`open_sidebar`、`login`/`logout` 这些高频方法，它们封装了完整的多步操作流程，直接调用即可，无需重复用基础AW逐步拼装。
>
> **造数原则：** 如果用例的 `setup()` 需要准备测试数据（如创建测试群、让对端先发一条消息），优先使用 `user.cli` 的造数方法（第六章），而不是驱动 UI 完成这些操作。造数方法速度快、不受 App 页面状态影响，可以显著提升用例稳定性。
