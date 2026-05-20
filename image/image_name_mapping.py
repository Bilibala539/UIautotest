import os

path = r"E:\UIAutotest\image"
test_path = r"E:\UIAutotest\image_ai"


LOGIN_POPO_TEXT = os.path.join(path, "登录页-网易popo文案.png")
HOME_POPO_LOGO = os.path.join(path, "桌面-logo.png")
LOGIN_READ_CENTER_FALSE = os.path.join(path, "登录页-阅读同意勾选框-未勾选.png")
LOGIN_READ_CENTER_TRUE = os.path.join(path, "登录页-阅读同意勾选框-已勾选.png")
LOGIN_ENTER = os.path.join(path, "登录页-登录按钮.png")
MESSAGE_TAB_BLUE = os.path.join(test_path, "消息tab页-导航栏消息蓝色高亮.png")
MESSAGE_TAB_GRUE = os.path.join(path, "消息tab页-导航栏消息灰色.png")
MESSAGE_TAB_MSG_TEXT = os.path.join(test_path, "消息tab页-左上角消息文案.png")
MESSAGE_TAB_SEARCH = os.path.join(path, "会话列表页-搜索按钮.png")

# 侧边栏
SIDEBAR_SETTINGS = os.path.join(path, "侧边栏-设置.png")

# 设置页
SETTINGS_LOGOUT = os.path.join(test_path, "设置页-退出登录.png")
SETTINGS_LOGOUT_CONFIRM = os.path.join(path, "退登确认弹窗-退出登录.png")
SETTINGS_MESSAGE_ENTRY = os.path.join(test_path, "设置页-消息入口.png")

# 消息设置页
MSG_SETTINGS_TITLE = os.path.join(test_path, "消息设置页-页面标题消息.png")
MSG_SETTINGS_SWITCH_ON = os.path.join(path, "消息设置页-开关-开启状态.png")
MSG_SETTINGS_SWITCH_OFF = os.path.join(path, "消息设置页-开关-关闭状态.png")

# 中心弹窗
POPO_POP = os.path.join(path, "中心弹窗-悬浮窗权限弹窗.png")
POPO_POP_OK = os.path.join(path, "中心弹窗-确定按钮.png")
POPO_POP_CANCEL = os.path.join(path, "中心弹窗-悬浮窗权限弹窗-取消按钮.png")
OPEN_DOOR_BLUETOOTH_POP_CANCEL = os.path.join(path, "移动开门-蓝牙弹窗-取消按钮.png")

# 会话列表页
SESSIONLIST_PLUS_BUTTON = os.path.join(path, "会话列表页右上角+按钮.png")
SESSIONLIST_PLUS_BUTTON_CREATETEAM = os.path.join(path, "会话列表页右上角+菜单-创建群聊.png")
ICON_FUWUHAO = os.path.join(path, "服务号标签icon.png")

# 会话窗口页
MSG_P2P_UNDER_BOTTON = os.path.join(path, "p2p底部快捷按钮.png")
MSG_P2P_CELL_BOTTON = os.path.join(path, "p2p-右上角音视频icon.png")
MSG_RECELL_POP = os.path.join(path, "撤回消息确认弹窗.png")
MSG_FILE_JSON = os.path.join(path, "会话窗口-json文件.png")
MSG_FILE_VIDEO = os.path.join(path, "会话窗口-视频文件.png")
MSG_UNREAD_ICON = os.path.join(path, "会话窗口-未读icon.png")
MSG_GOOD = os.path.join(path, "会话窗口-赞按钮.png")
MSG_MESSAGE_GOOD = os.path.join(path, "会话窗口-赞消息.png")

# ==================== 聊天页 - 扩展编辑（富文本） ====================
CHAT_PARAGRAPH_BUTTON = os.path.join(test_path, "聊天页-段落按钮.png")
EXTENDED_EDIT_BOLD_B = os.path.join(test_path, "扩展编辑-加粗B按钮.png")
EXTENDED_EDIT_ITALIC_I = os.path.join(path, "扩展编辑-斜体I按钮.png")
EXTENDED_EDIT_UNDERLINE_U = os.path.join(path, "扩展编辑-下划线U按钮.png")
EXTENDED_EDIT_STRIKETHROUGH_S = os.path.join(path, "扩展编辑-删除线S按钮.png")
EXTENDED_EDIT_FONT_COLOR_A = os.path.join(path, "扩展编辑-字色A按钮.png")
EXTENDED_EDIT_STYLE_6 = os.path.join(path, "扩展编辑-样式6按钮.png")
# EXTENDED_EDIT_MARKDOWN — 已废弃：当前版本扩展编辑工具栏中不存在此按钮
# EXTENDED_EDIT_CLOSE_BUTTON — 已废弃：当前版本扩展编辑工具栏中不存在此按钮
EXTENDED_EDIT_SEND_BUTTON = os.path.join(path, "扩展编辑-发送按钮.png")
EXTENDED_EDIT_STYLE_TOOLBAR = os.path.join(path, "扩展编辑-样式工具栏.png")

# ==================== 聊天页 ====================
CHAT_SEND_BUTTON = os.path.join(path, "聊天页-发送按钮.png")
CHAT_PLUS_BUTTON = os.path.join(path, "聊天页-更多加号按钮.png")
CHAT_PLUS_FILE = os.path.join(path, "聊天页-更多加号-文件.png")
# 聊天页图片编辑相关（已验证）
CHAT_PLUS_ALBUM = os.path.join(path, "聊天页-更多加号-相册.png")
CHAT_SENT_IMAGE_BUBBLE = os.path.join(path, "聊天页-已发送图片气泡.png")
ALBUM_PREVIEW_EDIT_BUTTON = os.path.join(path, "相册预览页-编辑按钮.png")
ALBUM_PREVIEW_SEND_BUTTON = os.path.join(path, "相册预览页-发送按钮.png")
IMAGE_EDITOR_TOOLBAR = os.path.join(path, "图片编辑器-底部工具栏.png")
IMAGE_EDITOR_DONE_BUTTON = os.path.join(path, "图片编辑器-完成按钮.png")
IMAGE_EDITOR_PEN_BUTTON = os.path.join(path, "图片编辑器-画笔按钮.png")
IMAGE_EDITOR_FORWARD = os.path.join(path, "图片编辑器-完成-转发icon.png")
IMAGE_EDITOR_H = os.path.join(path, "图片编辑器-H.png")

# 长按菜单相关（已验证通过）
CHAT_REPLY_QUOTE_BAR = os.path.join(path, "聊天页-回复引用栏.png")
CHAT_REPLY_QUOTE_CLOSE = os.path.join(path, "聊天页-引用关闭按钮.png")
CHAT_COPY_SUCCESS_TOAST = os.path.join(test_path, "聊天页-复制成功toast.png")
CHAT_MULTI_SELECT_TITLE = os.path.join(path, "聊天页-多选模式标题栏.png")
CHAT_TRANSLATE_RESULT = os.path.join(path, "聊天页-翻译结果文案.png")
CHAT_FAVORITE_TOAST = os.path.join(path, "聊天页-已收藏提示.png")



# 小程序
KM_ICON = os.path.join(path, "网易KM-头像.png")
KM_LOGO = os.path.join(path, "网易KM-logo.png")
RN_CLOSE = os.path.join(path, "RN小程序-关闭按钮.png")
OPEN_DOOR_ICON = os.path.join(path, "移动开门icon.png")
OPEN_DOOR_LOGO = os.path.join(path, "移动开门-logo.png")
OPEN_DOOR_CLOSE = os.path.join(path, "移动开门-关闭按钮.png")

# 选人组件
SELECT_TITLE_ADD_TEAM_MUNBER = os.path.join(path, "选人组件头部-添加群成员.png")
SELECT_CONTACTR_TAB = os.path.join(path, "选人组件-联系人tab.png")
SELECT_SEARCH = os.path.join(path, "选人组件-搜索框.png")
SELECT_OK_BLUE = os.path.join(path, "选人组件-确认按钮蓝色.png")
SELECT_CIRCLE = os.path.join(path, "选人组件-圆形勾选框.png")
SELECT_CIRCLE_BLUE = os.path.join(path, "选人组件-圆形勾选框-蓝色.png")
SELECT_CANCEL = os.path.join(path, "选人组件-左上角关闭按钮.png")

# 选择已有群组
CREATE_NEW_TEAM = os.path.join(path, "选择已有群组-创建新的群组.png")

# 大搜
SEARCH_INPUT_ICON = os.path.join(path, "会话列表页-搜索按钮.png")
SEARCH_CANCEL = os.path.join(path, "搜索页面-输入框右侧取消.png")
SEARCH_AI = os.path.join(path, "搜索页面-AI icon.png")
SEARCH_EMPTY = os.path.join(path, "搜索页面-空态图片.png")

SEARCH_TAB1 = os.path.join(path, "搜索页面-全部tab.png")
SEARCH_TAB2 = os.path.join(path, "搜索页面-联系人tab.png")
SEARCH_TAB2_NO = os.path.join(path, "搜索页面-联系人tab-未选中.png")
SEARCH_TAB3 = os.path.join(path, "搜索页面-群tab.png")
SEARCH_TAB3_NO = os.path.join(path, "搜索页面-群tab-未选中.png")
SEARCH_TAB3_BOTTON = os.path.join(path, "默认排序包含成员下拉按钮.png")
SEARCH_TAB4 = os.path.join(path, "搜索页面-消息tab.png")
SEARCH_TAB4_BOTTON = os.path.join(path, "搜索页面-消息tab-条件按钮.png")
SEARCH_TAB4_NO = os.path.join(path, "搜索页面-消息tab-未选中.png")
SEARCH_TAB5 = os.path.join(path, "搜索页面-日程tab.png")
SEARCH_TAB5_NO = os.path.join(path, "搜索页面-日程tab-未选中.png")
SEARCH_TAB6 = os.path.join(path, "搜索页面-云空间tab.png")
SEARCH_TAB6_NO = os.path.join(path, "搜索页面-云空间tab-未选中.png")
SEARCH_TAB7 = os.path.join(path, "搜索页面-任务tab.png")
SEARCH_TAB7_NO = os.path.join(path, "搜索页面-任务tab-未选中.png")
SEARCH_TAB8 = os.path.join(path, "搜索页面-应用tab.png")
SEARCH_TAB8_NO = os.path.join(path, "搜索页面-应用tab-未选中.png")

SEARCH_ALL_LXR = os.path.join(path, "搜索结果页-全部tab-联系人部分.png")
SEARCH_ALL_QUN = os.path.join(path, "搜索结果页-全部tab-群部分.png")
SEARCH_ALL_MSG = os.path.join(path, "搜索结果页-全部tab-消息部分.png")
SEARCH_ALL_YKJ = os.path.join(path, "搜索结果页-全部tab-云空间部分.png")

SEARCH_RESULT_KM = os.path.join(path, "网易KM搜索结果.png")
SEARCH_RESULT_OPEN_DOOR = os.path.join(path, "移动开门搜索结果.png")
SEARCH_RESULT_AYU = os.path.join(path, "阿鱼搜索结果.png")
SEARCH_RESULT_GZXZZS = os.path.join(path, "广州行政助手搜索结果.png")

SEARCH_WANGYING_BLUE = os.path.join(path, "王英-蓝色高亮.png")
SEARCH_WANGYING43_BLUE = os.path.join(path, "wangying43-蓝色高亮.png")
SEARCH_WANGYING_HEAD = os.path.join(path, "王英头像彩色.png")

SEARCH_CESHI_BLUE = os.path.join(test_path, "测试-蓝色高亮.png")
SEARCH_123_BLUE = os.path.join(path, "123-蓝色高亮.png")
SEARCH_GRPPOPOQA_BLUE = os.path.join(path, "grp.popoqa蓝色高亮.png")

# 侧边栏
SIDEBAR_MY_COLLECTION = os.path.join(test_path, "侧边栏-我的收藏.png")
SIDEBAR_DEVICE_MANAGEMENT = os.path.join(path, "侧边栏-登录设备管理.png")
SIDEBAR_SETTINGS_BUTTON = os.path.join(test_path, "侧边栏-设置按钮.png")
SIDEBAR_SERVICE_DESK = os.path.join(path, "侧边栏-服务台.png")

# 个人资料页
PROFILE_PAGE_NAME = os.path.join(path, "个人资料页-用户名.png")

# ==================== 长按菜单 ====================
LONGPRESS_FAVORITE_BUTTON = os.path.join(path, "长按菜单-收藏按钮.png")
LONGPRESS_FAVORITE_TEXT = os.path.join(path, "长按菜单-收藏文字.png")

TOAST_SENDED = os.path.join(path, "已发送_toast.png")

# ==================== 易生活页 ====================
ELIFE_MORE_BUTTON = os.path.join(path, "易生活页-更多按钮.png")
ELIFE_FLOATING_ICON = os.path.join(path, "易生活页-浮窗图标.png")

# ==================== 系统级 ====================
FILE_SELECT_MORE = os.path.join(path, "文件选择器-左上角更多按钮.png")
FILE_SELECT_MORE_OPENICON = os.path.join(path, "文件选择器-更多侧边栏-打开文档图标.png")
FILE_SELECT_MORE_SEARCH = os.path.join(path, "文件选择器-搜索按钮.png")


# ==================== 群设置页（草稿 - 待验证） ====================
GROUP_ANNOUNCEMENT_EMPTY_PLACEHOLDER = os.path.join(path, "群公告编辑页-空公告输入框占位符.png")

# ==================== 通讯录页 ====================
CONTACTS_TITLE_TEXT = os.path.join(path, "通讯录页-左上角通讯录文案.png")
CONTACTS_SEARCH_BUTTON = os.path.join(path, "通讯录页-搜索按钮.png")
CONTACTS_ADD_BUTTON = os.path.join(path, "通讯录页-添加按钮.png")
CONTACTS_GROUP_ENTRY = os.path.join(path, "通讯录页-联系人分组入口.png")
CONTACTS_TEAM_ENTRY = os.path.join(path, "通讯录页-群组入口.png")
CONTACTS_SERVICE_ENTRY = os.path.join(path, "通讯录页-服务号入口.png")
CONTACTS_ALPHABET_BAR = os.path.join(path, "通讯录页-字母索引栏.png")

# 通讯录页 - 底部导航栏
CONTACTS_NAV_MESSAGE_TAB = os.path.join(path, "通讯录页-底部导航栏消息tab.png")
CONTACTS_NAV_CALENDAR_TAB = os.path.join(path, "通讯录页-底部导航栏日历tab.png")
CONTACTS_NAV_CLOUD_TAB = os.path.join(path, "通讯录页-底部导航栏云空间tab.png")
CONTACTS_NAV_WORKSPACE_TAB = os.path.join(path, "通讯录页-底部导航栏工作台tab.png")
CONTACTS_NAV_ELIFE_TAB = os.path.join(path, "通讯录页-底部导航栏易生活tab.png")
CONTACTS_NAV_MORE_TAB = os.path.join(path, "通讯录页-底部导航栏更多tab.png")

# 会话分组
SESSION_GROUP_MORE_BUTTON = os.path.join(test_path, "消息tab页-分组更多按钮.png")

# ==================== 日历模块 - 三日视图（草稿 - 待 verify 转正） ====================
# 注意：链接实际文案为"去任务中查看"（非知识库写的"去日历本中查看"），文件名按实际命名
# 仅供已 DEPRECATED 的旧 AW (_open_calendar_sidebar / 旧 create_calendar_book 等) 引用，新代码不要用
CALENDAR_SIDEBAR_BUTTON = os.path.join(test_path, "日历页-侧边栏按钮.png")
CALENDAR_SUBTAB_CAL = os.path.join(test_path, "日历页-子Tab-日历选中.png")
CALENDAR_SUBTAB_ROOM = os.path.join(test_path, "日历页-子Tab-会议室未选中.png")
CALENDAR_ADD_PLUS = os.path.join(test_path, "日历页-右下角添加按钮.png")
CALENDAR_GOTO_BOOK_LINK = os.path.join(test_path, "日历页-去任务中查看链接.png")
CALENDAR_UTC_LABEL = os.path.join(test_path, "日历页-UTC时区标识.png")

# ==================== 日历模块 - 任务管理页（即知识库的 calendar_book_page，草稿 - 待 verify 转正） ====================
# 注意：这版 POPO 中"日历本管理"页实际呈现为"任务"页（标题"任务"，含全部任务/快捷方式/我关注的/我创建的/全部项目）
# 常量名沿用 CAL_BOOK_* 以保持与原 spec 一致，但 UI 文案对应"任务管理"
CAL_BOOK_SEARCH_ICON = os.path.join(test_path, "任务管理页-右上角搜索图标.png")
CAL_BOOK_MY_FOLLOWED = os.path.join(test_path, "任务管理页-我关注的行.png")
CAL_BOOK_MY_CREATED = os.path.join(test_path, "任务管理页-我创建的行.png")
CAL_BOOK_CREATE_PLUS = os.path.join(test_path, "任务管理页-右下角创建按钮.png")

# ==================== 日历模块 - 我创建的页（草稿 - 待 verify 转正） ====================
# 注意：实际 UI 是"筛选标签条"（未完成×/截止时间▾/优先级▾/↕创建时），非知识库写的"筛选 ▾/排序 ▾"两个下拉
# FILTER 取"截止时间 ▾"作为筛选语义代表；SORT 取右侧"↕ 创建时"含排序图标（"间"字被源 UI 自身截断）
CAL_MY_CREATED_FILTER = os.path.join(test_path, "我创建的页-截止时间筛选.png")
CAL_MY_CREATED_SORT = os.path.join(test_path, "我创建的页-创建时间排序.png")
CAL_MY_CREATED_PLUS = os.path.join(test_path, "我创建的页-右下角创建按钮.png")


