# UIAutotest AW方法总结与复用指南

> **核心原则：编写新用例或新业务AW时，必须先查阅本文档，已封装的功能直接调用，避免重复实现。**

---

## 一、架构层级总览

```
PPUser (用户入口，user.py)
  └── user.aw → AWHelper (aw_helper.py)
        ├── MuMuBusiness (business/mumu.py)    ← Android 端业务方法
        ├── CommonBusiness (business/common.py) ← 通用业务方法
        └── AWBase (aw_base.py)                 ← 基础操作(OCR/图像/点击/滑动)
```

**调用链路**：`self.userA.send_message(...)` → `PPUser.send_message()` → `self.aw.send_message()` → `MuMuBusiness.send_message()`

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

### 4.4 🔄 撤回消息 `recall_message(message_text)`

**前置条件：** 当前在聊天页面，消息为自己发送且24小时内。

**完整流程：**
1. `long_press_text(message_text)` — OCR定位消息文字并长按(1.5秒)
2. `find_text_by_ocr(message_text)` — 获取消息y坐标，用于后续验证区域计算
3. `click_text("撤回", region=HALF_DOWN)` — 在底部弹出的操作菜单中点击"撤回"
4. `image_exists(MSG_RECELL_POP)` → `click_text("确定")` — 如果有确认弹窗则点确定
5. `find_text_by_ocr("你撤回了一条消息")` — **验证撤回成功：出现撤回提示**

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
1. `long_press_text(message_text, duration=1.5)` — 长按目标消息
2. `click_text("复制", region=HALF_DOWN)` — 点击弹出菜单中的"复制"
3. `image_exists(CHAT_COPY_SUCCESS_TOAST)` — **验证：复制成功toast**

**验证的图片：** `CHAT_COPY_SUCCESS_TOAST`(复制成功提示)

**业务作用：** 复制消息文字内容到系统剪贴板。

---

### 4.4c ☑️ 多选消息 `multi_select_message(message_text)`

**前置条件：** 当前在聊天页面。

**完整流程：**
1. `long_press_text(message_text, duration=1.5)` — 长按目标消息
2. `click_text("多选", region=HALF_DOWN)` — 点击弹出菜单中的"多选"
3. `image_exists(CHAT_MULTI_SELECT_TITLE, region=HALF_UP)` — **验证：进入多选模式**
4. `press_back()` — 退出多选模式

**验证的图片：** `CHAT_MULTI_SELECT_TITLE`(多选模式标题栏"已选中")

**业务作用：** 进入多选模式并退出，验证多选功能可用。

---

### 4.4d 🌐 翻译消息 `translate_message(message_text)`

**前置条件：** 当前在聊天页面。

**完整流程：**
1. `long_press_text(message_text, duration=1.5)` — 长按目标消息
2. `click_text("翻译", region=HALF_DOWN)` — 点击弹出菜单中的"翻译"
3. `image_exists(CHAT_TRANSLATE_RESULT, region=HALF_DOWN)` — **验证：翻译结果出现**

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

### 4.12 应用控制

| 方法 | 作用 |
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
| `user.input_text(text)` | 输入文本 |
| `user.tap(x, y, ...)` | 点击坐标 |
| `user.wait_and_click_text(text, timeout)` | 等待文字出现再点击 |
| `user.wait_and_click_image(image_name, timeout)` | 等待图片出现再点击 |

---

## 六、复用指南 — 编写新用例时的正确姿势

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
| 需要创建群聊 | `user.create_team()` | 完整的建群流程 |
| 需要查看个人资料 | `user.view_my_profile()` | 返回资料字典 |

---

## 七、图片常量索引

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

## 八、搜索区域常量 (search_region.py)

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

## 九、尚未实现的功能（需要新建AW）

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
