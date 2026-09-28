# -*- coding: utf-8 -*-
"""Ground-truth labels for the 93 OCR'd screenshots.

label_basis:
  viewed  = 人工查看截图确认（本 POC 中由 agent 直接看图核实）
  ocr_pat = OCR 文本模式与页面特征一一对应（如 电台页的"搜索电台/全国电台/北京交通广播"）
  name    = 文件名即标签且与 OCR 内容一致
不确信的样本一律不入表。
"""

PAGES = {
    "home_recommend": "首页推荐标签页：顶部有推荐/音乐/AI/可视音箱/电台标签栏，搜索框为跨平台搜索音乐，页面有QQ音乐/网易云/酷狗等平台入口、我喜欢、歌单、AI卡片、最近播放、推荐音乐区块",
    "home_music":     "首页音乐标签页：顶部有推荐/音乐/AI/可视音箱/电台标签栏，搜索框为跨平台搜索音乐，页面主体是QQ音乐/网易云音乐等平台的歌单封面网格列表",
    "home_radio":     "首页电台标签页：顶部有推荐/音乐/AI/可视音箱/电台标签栏，搜索框为搜索电台，页面有全国电台列表如北京交通广播1039、河北交通广播FM992、怀旧金曲964、石家庄交通广播",
    "home_vision":    "首页可视音箱标签页：顶部有推荐/音乐/AI/可视音箱/电台标签栏，页面有视觉窗口内容、手电筒样式的视觉效果等提示文字",
    "home_ai":        "首页AI对话标签页：顶部有推荐/音乐/AI/可视音箱/电台标签栏，页面有开场白、AI角色（小薇/惠声远等）、历史对话记录、添加更多AI角色",
    "me":             "我的页面：顶部是头像、昵称和手机号，下方有我的权益（权益中心、充值与消费记录、家庭管理、SWAN收藏）、设备管理（设备管理、音质设置），底部导航我的高亮",
    "device":         "设备页面：页面标题为设备，显示设备型号如HiVi M300MKII、WIFI状态、音源选择（Apple Music/QQ音乐等）、同步设备、DSP音效设置",
    "platform":       "平台页面：页面标题为平台，有充值明细、VIPB、数字资产余额0.49678500、充值按钮、各音乐平台授权列表（QQ音乐、AI平台、Spotify、酷狗音乐等）",
    "player":         "全屏播放页：界面以专辑封面和播放控制按钮为主，几乎没有文字，仅能看到少量进度时间文本",
    "playlist_page":  "歌单库页面：页面标题为歌单，有SWAN/QQ音乐/网易云音乐/酷狗平台筛选标签、创建和聚合切换、歌单列表（我的家庭、我的音乐）、已加载全部",
    "playlist_detail":"歌单详情页：标题为歌单名如我的家庭，显示0首歌、收藏全部、全部、来源统计（QQ音乐0首 网易云0首）、暂无歌曲快去添加",
    "collection":     "SWAN收藏页面：页面标题为SWAN收藏，列表有我的家庭、我的音乐两个收藏歌单，底部有添加新的收藏歌单按钮",
    "history":        "播放历史页面：顶部有搜索框和单曲/专辑/歌单/电台等分类标签，下方是播放历史记录列表",
    "sheet_device":   "设备切换弹层：在当前页面之上弹出切换设备面板，列出可选设备单选项（Libretto、HiVi M300MKII、Apple Music、手机蓝牙耳机）",
    "volume_popup":   "音量调节弹层：屏幕上显示音量弹窗，有当前音量数字、关闭按钮X、设备名（Speaker）、加减号",
    "login":          "登录页面：页面有SWAN天鹅logo、登入后就可畅享音乐世界、+86手机号输入框、下一步按钮、已经阅读并同意隐私政策和使用政策、验证码登录或密码登入",
    "auth_dialog":    "授权通知弹层：标题授权通知，内容为只有经过授权的音乐平台才能搜索歌曲，列出QQ音乐、网易云音乐各自的授权按钮，底部有更多平台",
    "ai_role_settings":"AI角色设置页面：页面标题为所有角色，分系统和自定义两组角色列表（你好,我是你的应用助手,惠威百科 / 你的好朋友,小薇等），底部有添加更多AI角色按钮",
    "person_info":    "个人信息修改页面：标题个人信息修改，有头像、昵称、性别、手机号、注销账号、退出登录",
    "avatar_popup":   "基本信息修改弹窗：标题基本信息修改，有头像、昵称、性别、手机号、注销账号、退出登录，底部有保存和取消按钮、从手机相册选取",
    "profile_edit":   "修改昵称页面：标题修改昵称，有昵称输入框，屏幕下方是全键盘字母按键",
    "area_code":      "区号选择页面：标题选择国家地区，列表为中国+86、中国香港+852、中国澳门+853、中国台湾+886、美国等",
}

# (相对 explorer_output 的路径, 标签, 依据)
LABELS = [
    # ---- home_recommend ----
    ("verify_run3/tab_推荐.png",                     "home_recommend", "viewed"),
    ("verify_run3/fix_HOME_SEARCH_BAR.png",          "home_recommend", "ocr_pat"),
    ("aw_element_tmp/recap11/home_music.png",        "home_recommend", "viewed"),  # 文件名误：实为推荐tab
    ("aw_element_tmp/recap11/home_recommend.png",    "home_recommend", "ocr_pat"),
    ("aw_element_tmp/recap12/recommend.png",         "home_recommend", "ocr_pat"),
    ("aw_element_tmp/recap12/tab_recommend.png",     "home_recommend", "ocr_pat"),
    ("verify_regression1/state_home.png",            "home_recommend", "ocr_pat"),
    ("verify_regression1/state_home2.png",           "home_recommend", "ocr_pat"),
    ("verify_regression1/state_restored.png",        "home_recommend", "ocr_pat"),
    ("verify_regression1/final_home.png",            "home_recommend", "ocr_pat"),
    ("verify_regression1/probe1.png",                "home_recommend", "ocr_pat"),
    ("verify_regression1/probe_top.png",             "home_recommend", "ocr_pat"),
    ("aw_element_tmp/domain3/home.png",              "home_recommend", "ocr_pat"),
    ("aw_element_tmp/domain3/final_home.png",        "home_recommend", "ocr_pat"),
    ("aw_element_tmp/recap11/final_home.png",        "home_recommend", "ocr_pat"),
    ("aw_element_tmp/recap12/final_home.png",        "home_recommend", "ocr_pat"),
    ("aw_element_tmp/castsheet/home.png",            "home_recommend", "ocr_pat"),
    ("verify_run3/state_after_back.png",             "home_recommend", "ocr_pat"),
    ("verify_run3/after_relaunch_full.png",          "home_recommend", "ocr_pat"),
    ("aw_element_tmp/final_state.png",               "home_recommend", "ocr_pat"),
    ("aw_element_tmp/recap11/current.png",           "home_recommend", "ocr_pat"),
    # ---- home_music ----
    ("verify_run3/tab_音乐.png",                     "home_music", "name"),
    ("aw_element_tmp/src_home_music.png",            "home_music", "viewed"),
    ("aw_element_tmp/recap12/music.png",             "home_music", "ocr_pat"),
    ("aw_element_tmp/recap12/tab_music.png",         "home_music", "ocr_pat"),
    # ---- home_radio ----
    ("verify_run3/tab_电台.png",                     "home_radio", "name"),
    ("verify_run3/fix_RADIO_SEARCH_BAR.png",         "home_radio", "ocr_pat"),
    ("verify_run2/final_home.png",                   "home_radio", "viewed"),  # 文件名误：实为电台tab
    ("aw_element_tmp/src_home_radio.png",            "home_radio", "ocr_pat"),
    ("aw_element_tmp/src_home_recommend.png",        "home_radio", "viewed"),  # 文件名误：实为电台tab
    ("aw_element_tmp/recap12/radio.png",             "home_radio", "ocr_pat"),
    ("aw_element_tmp/recap12/tab_radio.png",         "home_radio", "ocr_pat"),
    # ---- home_vision ----
    ("verify_run3/tab_可视音箱.png",                 "home_vision", "name"),
    ("verify_run3/fix_VISION_HINT.png",              "home_vision", "ocr_pat"),
    ("aw_element_tmp/src_home_vision.png",           "home_vision", "ocr_pat"),
    ("aw_element_tmp/recap12/vision.png",            "home_vision", "ocr_pat"),
    ("aw_element_tmp/recap12/tab_vision.png",        "home_vision", "ocr_pat"),
    # ---- home_ai ----
    ("verify_run3/tab_AI.png",                       "home_ai", "name"),
    ("verify_run3/fix_AI_ADD_ROLE.png",              "home_ai", "ocr_pat"),
    ("aw_element_tmp/src_home_ai.png",               "home_ai", "ocr_pat"),
    ("aw_element_tmp/recap12/ai.png",                "home_ai", "ocr_pat"),
    ("aw_element_tmp/recap12/tab_ai.png",            "home_ai", "ocr_pat"),
    # ---- me ----
    ("verify_run3/page_me.png",                      "me", "name"),
    ("verify_run3/FAIL_top_推荐.png",                "me", "viewed"),  # 文件名误：tab切换失败落在我页
    ("verify_run3/FAIL_top_音乐.png",                "me", "ocr_pat"),
    ("verify_run3/diag_after_goto_home.png",         "me", "viewed"),  # 文件名误：实为我页
    ("verify_run3/diag_before_sel_assert.png",       "me", "ocr_pat"),
    ("verify_run3/diag_before_sel_assert_music.png", "me", "ocr_pat"),
    ("verify_regression1/state_me.png",              "me", "name"),
    ("aw_element_tmp/recap11/me.png",                "me", "ocr_pat"),
    ("aw_element_tmp/src_me.png",                    "me", "ocr_pat"),
    # ---- device ----
    ("verify_run3/page_device.png",                  "device", "name"),
    ("verify_run3/after_select_card.png",            "device", "ocr_pat"),
    ("verify_run3/FAIL_select_card.png",             "device", "ocr_pat"),
    ("verify_regression1/state_device.png",          "device", "name"),
    ("aw_element_tmp/domain3/device_page.png",       "device", "name"),
    # ---- platform ----
    ("verify_run3/page_platform.png",                "platform", "name"),
    ("verify_regression1/state_platform.png",        "platform", "name"),
    ("aw_element_tmp/domain3/platform_page.png",     "platform", "name"),
    ("aw_element_tmp/recap11/platform.png",          "platform", "name"),
    # ---- player ----
    ("verify_regression1/state_player.png",          "player", "name"),
    ("verify_regression1/after_pytest1.png",         "player", "ocr_pat"),
    ("aw_element_tmp/domain3/player_full.png",       "player", "name"),
    ("aw_element_tmp/domain3/device_selected.png",   "player", "ocr_pat"),  # 新构建卡片点击=进播放页
    ("aw_element_tmp/domain3/loop_state_0.png",      "player", "ocr_pat"),
    ("aw_element_tmp/domain3/loop_state_1.png",      "player", "ocr_pat"),
    ("aw_element_tmp/domain3/loop_state_2.png",      "player", "ocr_pat"),
    ("aw_element_tmp/domain3/loop_state_3.png",      "player", "ocr_pat"),
    # ---- playlist_page ----
    ("aw_element_tmp/domain3/after_gedan_click.png", "playlist_page", "viewed"),
    # ---- playlist_detail ----
    ("aw_element_tmp/domain3/playlist_detail.png",   "playlist_detail", "ocr_pat"),
    # ---- collection ----
    ("verify_run3/FAIL_top_AI.png",                  "collection", "viewed"),  # 文件名误：实为SWAN收藏页
    ("verify_run3/FAIL_top_可视音箱.png",            "collection", "ocr_pat"),
    ("verify_run3/FAIL_top_电台.png",                "collection", "ocr_pat"),
    # ---- history ----
    ("aw_element_tmp/recap11/history.png",           "history", "ocr_pat"),
    # ---- sheet_device ----
    ("verify_regression1/state_sheet.png",           "sheet_device", "name"),
    ("aw_element_tmp/domain3/sheet.png",             "sheet_device", "name"),
    ("aw_element_tmp/recap11/sheet.png",             "sheet_device", "name"),
    ("aw_element_tmp/castsheet/sheet.png",           "sheet_device", "name"),
    ("aw_element_tmp/castsheet/sheet_fresh.png",     "sheet_device", "name"),
    # ---- volume_popup ----
    ("verify_regression1/state_volume_popup.png",    "volume_popup", "name"),
    ("verify_regression1/volume_minus5.png",         "volume_popup", "ocr_pat"),
    ("aw_element_tmp/domain3/volume_popup.png",      "volume_popup", "name"),
    # ---- login ----
    ("aw_element_tmp/domain3/playlist_page.png",     "login", "viewed"),  # 文件名误：实为登录页
    ("aw_element_tmp/domain3/setup_unknown.png",     "login", "ocr_pat"),
    ("aw_element_tmp/domain3/final_state.png",       "login", "ocr_pat"),
    ("aw_element_tmp/domain3/after_login_fail.png",  "login", "ocr_pat"),
    # ---- auth_dialog ----
    ("verify_run3/search_retrigger_state.png",       "auth_dialog", "viewed"),
    ("verify_run3/state_before_back.png",            "auth_dialog", "ocr_pat"),
    # ---- ai_role_settings ----
    ("aw_element_tmp/smoke_ai_role_settings_page.png","ai_role_settings", "viewed"),
    # ---- person_info / avatar_popup / profile_edit / area_code ----
    ("aw_element_tmp/src_person_info.png",           "person_info", "ocr_pat"),
    ("aw_element_tmp/src_avatar_popup.png",          "avatar_popup", "ocr_pat"),
    ("aw_element_tmp/src_profile_edit.png",          "profile_edit", "ocr_pat"),
    ("aw_element_tmp/src_area_code.png",             "area_code", "ocr_pat"),
]

# 页面级归并（home 各 tab → home），用于次要指标
PAGE_GROUP = {
    "home_recommend": "home", "home_music": "home", "home_radio": "home",
    "home_vision": "home", "home_ai": "home",
}
