"""平台隔离的图片路径与图片转正工具。

图片按 ``image/<platform>`` 与 ``image_ai/<platform>`` 分开保存。新截图
先登记到草稿目录，验证通过后调用 ``promote_image`` 转移到正式目录。
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORMAL_IMAGE_ROOT = PROJECT_ROOT / "image"
DRAFT_IMAGE_ROOT = PROJECT_ROOT / "image_ai"
SUPPORTED_PLATFORMS = ("web", "android", "flutter")


def normalize_platform(platform: Optional[str] = None) -> str:
    """返回受支持的平台名称。"""
    value = (platform or os.environ.get("PLATFORM", "web")).strip().lower()
    if value not in SUPPORTED_PLATFORMS:
        raise ValueError(
            f"不支持的平台: {value!r}；可选值: {', '.join(SUPPORTED_PLATFORMS)}"
        )
    return value


def get_image_dir(platform: Optional[str] = None, draft: bool = False) -> Path:
    """获取指定平台的正式或草稿图片目录，并确保目录存在。"""
    root = DRAFT_IMAGE_ROOT if draft else FORMAL_IMAGE_ROOT
    directory = root / normalize_platform(platform)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def image_path(
    filename: str,
    platform: Optional[str] = None,
    draft: bool = False,
) -> str:
    """生成平台图片路径，禁止路径穿越和绝对路径覆盖。"""
    relative_path = Path(filename)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("图片文件名必须是平台目录内的相对路径")
    root = get_image_dir(platform, draft=draft).resolve()
    candidate = (root / relative_path).resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError("图片路径必须位于平台图片目录内")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return str(candidate)


def promote_image(
    filename: str,
    platform: Optional[str] = None,
    overwrite: bool = False,
) -> str:
    """将平台图片从 image_ai 转正到 image，并返回正式路径。"""
    source = Path(image_path(filename, platform=platform, draft=True))
    target = Path(image_path(filename, platform=platform, draft=False))
    if not source.is_file():
        raise FileNotFoundError(f"找不到待转正图片: {source}")
    if target.exists() and not overwrite:
        raise FileExistsError(f"正式图片已存在: {target}；如需覆盖请传入 overwrite=True")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    return str(target)


def demote_image(filename: str, platform: Optional[str] = None, overwrite: bool = False) -> str:
    """将平台图片从 image 退回 image_ai，便于重新验证。"""
    source = Path(image_path(filename, platform=platform, draft=False))
    target = Path(image_path(filename, platform=platform, draft=True))
    if not source.is_file():
        raise FileNotFoundError(f"找不到正式图片: {source}")
    if target.exists() and not overwrite:
        raise FileExistsError(f"草稿图片已存在: {target}；如需覆盖请传入 overwrite=True")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    return str(target)


CURRENT_PLATFORM = normalize_platform()
WEB_IMAGE_DIR = str(get_image_dir("web"))
ANDROID_IMAGE_DIR = str(get_image_dir("android"))
FLUTTER_IMAGE_DIR = str(get_image_dir("flutter"))
WEB_DRAFT_IMAGE_DIR = str(get_image_dir("web", draft=True))
ANDROID_DRAFT_IMAGE_DIR = str(get_image_dir("android", draft=True))
FLUTTER_DRAFT_IMAGE_DIR = str(get_image_dir("flutter", draft=True))

# 保留旧变量名，但它们现在代表当前 PLATFORM 对应的平台目录。
path = str(get_image_dir(CURRENT_PLATFORM))
test_path = str(get_image_dir(CURRENT_PLATFORM, draft=True))


# =====================================================================
# Swan (Flutter) 元素图片
# 2026-09-08 真机验证（aw-verify，serial c0614b6a，720x1600）全部通过，
# 已由 promote_image 转正到 image/flutter/，常量登记为正式路径。
# =====================================================================

# --- 首页 (swan_首页) ---
SWAN_BOTTOM_PLAYER_BAR = image_path("swan_底部播放条.png", platform="flutter")

# --- 我的 (swan_我的页) ---
SWAN_ME_FAMILY_MANAGE_ROW = image_path("swan_我的_家庭管理行.png", platform="flutter")
SWAN_ME_FAVORITES_ROW = image_path("swan_我的_收藏行.png", platform="flutter")
SWAN_ME_DEVICE_MANAGE_ROW = image_path("swan_我的_设备管理行.png", platform="flutter")
SWAN_ME_SOUND_QUALITY_ROW = image_path("swan_我的_音质设置行.png", platform="flutter")

# --- 家庭管理 (swan_家庭管理页) ---
SWAN_FAMILY_ADD_MEMBER_ICON = image_path("swan_添加成员图标.png", platform="flutter")

# --- SWAN收藏 (swan_收藏页) ---
SWAN_FAV_FAMILY_GROUP_ROW = image_path("swan_收藏_我的家庭分组行.png", platform="flutter")
SWAN_FAV_MUSIC_GROUP_ROW = image_path("swan_收藏_我的音乐分组行.png", platform="flutter")
SWAN_FAV_ADD_PLAYLIST_BUTTON = image_path("swan_添加收藏歌单按钮.png", platform="flutter")

# --- 音质设置弹层 (swan_音质设置页) ---
SWAN_SOUND_QUALITY_DONE_BUTTON = image_path("swan_音质设置_完成按钮.png", platform="flutter")

# --- 验证码登录页 (swan_验证码登录页) ---
SWAN_LOGIN_PRIVACY_POLICY_LINK = image_path("swan_隐私政策链接.png", platform="flutter")
SWAN_LOGIN_USAGE_POLICY_LINK = image_path("swan_使用政策链接.png", platform="flutter")
SWAN_LOGIN_SUBMIT_BTN = image_path("swan_下一步按钮.png", platform="flutter")

# --- 验证码输入页 (swan_验证码输入页) ---
SWAN_LOGIN_CODE_FIELD_BOX = image_path("swan_验证码输入框.png", platform="flutter")

# --- 播放页 (swan_播放页) ---
SWAN_PLAYER_PLAY_PAUSE_BTN = image_path("swan_播放页_播放暂停按钮.png", platform="flutter")
SWAN_PLAYER_DISMISS_BTN = image_path("swan_播放页_收起按钮.png", platform="flutter")

# --- 设备页 (swan_设备页) ---
SWAN_DEVICE_ADD_BTN = image_path("swan_添加设备按钮.png", platform="flutter")

# --- 平台页 (swan_平台页) ---
# 2026-10-12 verify 转正：旧模板(9/24 未授权白底态)对已授权账号(189 恒为黄底/−号态)失效，
# 已从失败证据帧重截已授权态整行，平台页只读断言用例真机验证通过后 promote 覆盖。
# ⚠️ 行内副标题"雷泽大人 VIP"为 189 演示账号网易云授权昵称，对该账号持久稳定。
# ⚠️ 两态模板（2026-10-12）：本图=已授权态（189 演示号黄底+昵称，verify 转正）；
# 未授权态（135 测试号白底+「未授权」+黑[+]）另存 SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED
# （draft，待用例真机命中转正）。两态渲染差异大（行底色/副文案/右侧钮），勿混用。
SWAN_PLATFORM_NETEASE_ROW = image_path("swan_平台_网易云音乐行.png", platform="flutter")


# =====================================================================
# Swan (Flutter) Wave 1 元素图片（✅ 已转正）
# 2026-09-10 aw-element 采集（serial c0614b6a，720x1600），
# 源图与裁剪分析脚本见 explorer_output/aw_element_tmp/。
# 2026-09-10 aw-verify 真机走通验证（explorer_output/verify_wave1/），
# 14 张全部 click_image / image_exists 实测通过后 promote_image 转正。
# =====================================================================

# --- 首页顶 Tab 行（未选中态，用于 click_image 切换顶 Tab） ---
SWAN_HOME_TAB_RECOMMEND = image_path("swan_首页_推荐Tab按钮.png", platform="flutter")
SWAN_HOME_TAB_MUSIC = image_path("swan_首页_音乐Tab按钮.png", platform="flutter")
SWAN_HOME_TAB_RADIO = image_path("swan_首页_电台Tab按钮.png", platform="flutter")
SWAN_HOME_TAB_AI = image_path("swan_首页_AITab按钮.png", platform="flutter")
SWAN_HOME_TAB_VISION = image_path("swan_首页_可视音箱Tab按钮.png", platform="flutter")

# --- 首页各顶 Tab 内容区元素 ---
# ⚠️ SWAN_HOME_MUSIC_SEARCH_BAR 文件名沿用历史（原音乐 Tab 搜索条）；
# verify R2 起其 PNG 已同名重截为推荐 Tab 完整布局的搜索条（新构建音乐
# Tab 改歌单流，搜索条回归推荐 Tab），常量名不改、语义见 swan.py search()
SWAN_HOME_MUSIC_SEARCH_BAR = image_path("swan_首页音乐Tab_搜索条.png", platform="flutter")
SWAN_HOME_RADIO_SEARCH_BAR = image_path("swan_首页电台Tab_搜索条.png", platform="flutter")
SWAN_HOME_AI_ADD_ROLE = image_path("swan_首页AITab_添加角色入口.png", platform="flutter")
SWAN_HOME_AI_ROLE_SETTINGS = image_path("swan_首页AITab_角色设置入口.png", platform="flutter")
SWAN_HOME_VISION_UNBOUND_HINT = image_path("swan_首页可视音箱Tab_未绑定提示.png", platform="flutter")

# --- 我的页 ---
SWAN_ME_SCAN_ICON = image_path("swan_我的_扫一扫图标.png", platform="flutter")

# --- 资料编辑页 / 头像弹层 ---
SWAN_PROFILE_EDIT_DONE = image_path("swan_资料编辑_完成按钮.png", platform="flutter")
SWAN_PROFILE_EDIT_AVATAR_CANCEL = image_path("swan_资料编辑_头像弹层取消.png", platform="flutter")

# --- 区号选择页 ---
SWAN_AREA_CODE_CHINA_ROW = image_path("swan_区号选择_中国行.png", platform="flutter")


# =====================================================================
# Swan (Flutter) Wave 2 元素图片（2026-09-10 aw-verify 真机验证通过，已转正）
# 验证记录：explorer_output/verify_wave2/verify_wave2.py（s1-s6 全 PASS）
# =====================================================================

# --- 歌单页 (swan_歌单页) ---
SWAN_PLAYLIST_BACK_BTN = image_path("swan_歌单页_返回按钮.png", platform="flutter")
SWAN_PLAYLIST_CREATE_BTN = image_path("swan_歌单页_新建歌单按钮.png", platform="flutter")
SWAN_PLAYLIST_TAB_SWAN = image_path("swan_歌单页_SWAN平台Tab.png", platform="flutter")
# 新建歌单弹窗右上关闭按钮（aw-verify 2026-09-10 从 wave2 源图裁剪补充：弹窗无 key/desc/文案，
# press_back 实测不关闭，只能图定位；glyph 568,253-591,276）
SWAN_PLAYLIST_NEWDLG_CLOSE_BTN = image_path("swan_歌单页_新建歌单关闭按钮.png", platform="flutter")

# --- 歌单详情页 (swan_歌单详情页) ---
SWAN_PD_MORE_BTN = image_path("swan_歌单详情页_更多按钮.png", platform="flutter")
SWAN_PD_PLAY_ALL = image_path("swan_歌单详情页_播放全部.png", platform="flutter")  # ⚠️ 含"0首歌"计数，歌单加歌后需重截

# --- 我喜欢页 (swan_我喜欢页) ---
SWAN_FAVORITE_PLAY_ALL = image_path("swan_我喜欢页_播放全部.png", platform="flutter")  # ⚠️ 含"0首歌"计数，歌单加歌后需重截

# --- 播放历史页 (swan_播放历史页) ---
SWAN_HISTORY_TOPBAR = image_path("swan_播放历史页_顶栏.png", platform="flutter")
SWAN_HISTORY_TABBAR = image_path("swan_播放历史页_分类Tab条.png", platform="flutter")

# --- 切换设备弹层 (swan_切换设备弹层) ---
SWAN_DEVICE_SHEET_TITLE = image_path("swan_切换设备弹层_标题行.png", platform="flutter")

# --- 播放页 (swan_播放页) ---
SWAN_PLAYER_DEVICE_BTN = image_path("swan_播放页_设备切换按钮.png", platform="flutter")

# --- AI 对话页 (swan_AI对话页) ---
SWAN_AI_CHAT_VOICE_BTN = image_path("swan_AI对话页_语音按钮.png", platform="flutter")
SWAN_AI_CHAT_INPUT = image_path("swan_AI对话页_输入框.png", platform="flutter")


# =====================================================================
# Swan (Flutter) Wave 4 元素图片（平台/搜索域，✅ 已转正）
# 2026-09-10 aw-element 采集（serial c0614b6a，720x1600），
# 源图与裁剪分析脚本见 explorer_output/aw_element_tmp/wave4/。
# 2026-09-10 aw-verify 真机走通验证（explorer_output/aw_element_tmp/wave4_verify.py，
# 全链路 PASS，7 张全部 score=1.00@0.8）后 promote_image 转正。
# ⛔ 授权门禁两个主按钮仅用于 image_exists 防御性存在断言，禁止 click_image。
# =====================================================================

# --- 搜索输入页 (swan_搜索输入页) ---
SWAN_SEARCH_BACK = image_path("swan_搜索输入页_返回按钮.png", platform="flutter")
SWAN_SEARCH_SUBMIT = image_path("swan_搜索输入页_搜索按钮.png", platform="flutter")
SWAN_SEARCH_CLEAR = image_path("swan_搜索输入页_清空按钮.png", platform="flutter")

# --- 搜索结果页 (swan_搜索结果页) ---
SWAN_SEARCH_EMPTY = image_path("swan_搜索结果页_空态文案.png", platform="flutter")

# --- 授权门禁弹层 (swan_授权门禁弹层) ⛔ 只断言不点击 ---
SWAN_AUTH_GATE_LOGIN_BTN = image_path("swan_授权门禁弹层_授权登录按钮.png", platform="flutter")
SWAN_AUTH_GATE_ADD_BTN = image_path("swan_授权门禁弹层_添加按钮.png", platform="flutter")

# --- 平台页 (swan_平台页) ---
SWAN_PLATFORM_RADIO_ROW_ARROW = image_path("swan_平台_电台行箭头.png", platform="flutter")


# =====================================================================
# Swan (Flutter) Wave 5 元素图片（AI/Vision/视频域，✅ 已转正）
# 2026-09-10 aw-element 采集（serial c0614b6a，720x1600），
# 源图与裁剪分析脚本见 explorer_output/aw_element_tmp/wave5/。
# 2026-09-10 aw-verify 真机验证（explorer_output/verify_wave5/verify_wave5_awverify.py，
# 10/10 全部通过：4 项点击反应验证 + 6 项存在断言，score=1.00@0.8）后 promote_image 转正。
# ⛔ 红线：开始生成/上传照片卡（DIY 付费/相册）、完成按钮（角色编辑页，创建角色）、
#    平台行按钮（点击会弹「添加新平台」授权门禁）只断言不点击。
# =====================================================================

# --- 所有角色页 (swan_所有角色页) ---
SWAN_ALL_ROLES_MULTISELECT = image_path("swan_所有角色页_多选按钮.png", platform="flutter")

# --- 角色编辑页 (swan_角色编辑页，表单两屏长：完成在 swipe_up x3 后可见) ---
SWAN_ROLE_EDITOR_SELECT = image_path("swan_角色编辑页_选择按钮.png", platform="flutter")
SWAN_ROLE_EDITOR_MORE_PLATFORM = image_path("swan_角色编辑页_更多AI平台按钮.png", platform="flutter")
SWAN_ROLE_EDITOR_DONE = image_path("swan_角色编辑页_完成按钮.png", platform="flutter")  # ⛔ 只断言不点击

# --- AI 形象页 (swan_AI形象页) ---
SWAN_ROLE_IMAGES_DIY_BTN = image_path("swan_AI形象页_DIY形象按钮.png", platform="flutter")

# --- DIY 形象页 (swan_DIY形象页) ⛔ 只断言不点击（付费/相册） ---
SWAN_DIY_GENERATE_BTN = image_path("swan_DIY形象页_开始生成按钮.png", platform="flutter")  # ⛔ 只断言不点击
SWAN_DIY_UPLOAD_CARD = image_path("swan_DIY形象页_上传照片卡.png", platform="flutter")  # ⛔ 只断言不点击

# --- AI 平台管理页 (swan_AI平台管理页) ---
SWAN_AI_PLATFORM_ROW_BTN = image_path("swan_AI平台管理页_平台行按钮.png", platform="flutter")  # ⛔ 只断言不点击（点击会弹门禁）
SWAN_AI_PLATFORM_TITLE = image_path("swan_AI平台管理页_顶栏平台标题.png", platform="flutter")

# --- AI 历史页 (swan_AI历史页) ---
SWAN_AI_HISTORY_TITLE = image_path("swan_AI历史页_标题行.png", platform="flutter")


# =====================================================================
# Swan (Flutter) 回归第一批·域3 播放器元素图片（A12-A20）
# 2026-09-23 aw-codegen 按 docs/Swan回归用例AW实现方案.md §3 登记，
# PNG 由 aw-element 按 docs/agents/swan/aw-element.md 流程截取。
# 2026-09-24 aw-verify 真机实测（HONOR AKFDCP4718425500，720x1612，与采集
# 基线同机）：14 张存在断言全部 score=1.00@0.8（explorer_output/
# verify_regression1/），promote_image 转正，draft=True 改正式路径。
# ⚠️ SWAN_PLAYER_VOLUME_POPUP（含标题"Speaker<音量>"与滑条填充两处动态区）
#    与 SWAN_PLAYER_VOLUME_SLIDER（含动态填充）：音量=31%（截取态）时
#    score=1.00，音量±5 时 0.86/0.93，大幅偏离会失配——重裁建议见 verify 报告。
# 仍留草稿（PNG 未截，需播放任务）：SWAN_PLAYER_PAUSE_BTN（⏸ 态）、
#    SWAN_PLAYER_LOOP_SINGLE / SWAN_PLAYER_LOOP_SHUFFLE（循环三态之其余两态）。
# =====================================================================

# --- 播放页 播放控制（五键中的四键；▶ 态已有 SWAN_PLAYER_PLAY_PAUSE_BTN） ---
SWAN_PLAYER_PAUSE_BTN = image_path("swan_播放页_暂停按钮.png", platform="flutter")       # 播放中的 ⏸ 态圆钮
SWAN_PLAYER_PREV_BTN = image_path("swan_播放页_上一首按钮.png", platform="flutter")
SWAN_PLAYER_NEXT_BTN = image_path("swan_播放页_下一首按钮.png", platform="flutter")
SWAN_PLAYER_LOOP_LIST = image_path("swan_播放页_循环模式_列表循环.png", platform="flutter")     # 循环钮三态之一
SWAN_PLAYER_LOOP_SINGLE = image_path("swan_播放页_循环模式_单曲循环.png", platform="flutter", draft=True)
SWAN_PLAYER_LOOP_SHUFFLE = image_path("swan_播放页_循环模式_随机播放.png", platform="flutter", draft=True)
SWAN_PLAYER_PROGRESS_BAR = image_path("swan_播放页_进度条.png", platform="flutter")    # 进度条整条（滑条锚；勿含两端时间文字）

# --- 播放页 音量弹窗 ---
SWAN_PLAYER_VOLUME_ICON = image_path("swan_播放页_音量图标.png", platform="flutter")   # 播放页底部音量入口图标（与浅底变体内容全等，链内由 LIGHT 代表）
# ⚠️ 音量图标 glyph 极性随背景明度自适应（2026-09-29 element 三变体补截，
# run5 收口批次）：单模板跨背景必失配（同设备钮/加号钮/收起钮案），业务
# 改 _VOLUME_ICON_TEMPLATES 链式匹配（glyph→浅→深，见 SwanBusiness.
# _find_volume_icon）。
SWAN_PLAYER_VOLUME_ICON_GLYPH = image_path("swan_播放页_音量图标_glyph.png", platform="flutter", draft=True)
SWAN_PLAYER_VOLUME_ICON_LIGHT = image_path("swan_播放页_音量图标_浅底.png", platform="flutter", draft=True)
SWAN_PLAYER_VOLUME_ICON_DARK = image_path("swan_播放页_音量图标_深底.png", platform="flutter", draft=True)
SWAN_PLAYER_VOLUME_POPUP = image_path("swan_播放页_音量弹窗.png", platform="flutter")  # 弹窗右上角 X 关闭钮 36x36（存在性判据；非弹窗整体）
SWAN_PLAYER_VOLUME_SLIDER = image_path("swan_播放页_音量滑条.png", platform="flutter")  # ⚠️ 已废弃为几何锚（2026-09-28 run4d：填充态模板匹配矩形随音量漂移）——业务改 ± 钮锚定，留档不引用
SWAN_PLAYER_VOLUME_PLUS = image_path("swan_播放页_音量加号按钮.png", platform="flutter")   # 静态控件，滑条真轨道左界锚（见 SwanBusiness._find_volume_slider）
SWAN_PLAYER_VOLUME_MINUS = image_path("swan_播放页_音量减号按钮.png", platform="flutter")  # 静态控件，滑条真轨道右界锚

# --- 设备页 / 切换设备弹层 选中态 ---
# ⚠️ SWAN_DEVICE_CARD_SELECTED 已废弃（2026-09-28，业务代码停止引用）：
# test/profile 5.3.1 新构建点 WiFi 设备卡不再就地出现「选中标识」，而是
# 进全屏播放页（探索结论 knowledge/swan/draft/swan_设备详情页.md）；新口径
# 「当前输出」= 深色整卡容器 wifi_device_selected_<UUID>（动态 UUID 无法
# 截成模板），切换断言改走播放页页头/贴底播放条 OCR 设备名（见
# SwanBusiness.select_device）。登记保留仅作历史记录。
SWAN_DEVICE_CARD_SELECTED = image_path("swan_设备页_设备卡片选中态.png", platform="flutter")  # [废弃] 旧选中态口径，勿在新代码使用
SWAN_DEVICE_SHEET_CHECKED = image_path("swan_切换设备弹层_勾选态.png", platform="flutter")    # 行首勾选圆点选中态（知识库未见此态，需真机人工选一次以截取）

# --- 设备页 底栏切换设备入口 ---
# 底栏播放条最右 cast 图标（无键无文案，仅图模板可达），点击直达切换设备
# 弹层（不经过播放页）——explorer 已探明的输出切换最短路径
# （knowledge/swan/draft/swan_设备详情页.md 用例11 短路径结论）。
SWAN_BOTTOM_BAR_CAST_BTN = image_path("swan_底栏_切换设备钮.png", platform="flutter", draft=True)


# =====================================================================
# Swan (Flutter) 回归第一批·域4/7/8 元素图片（A21-A23 / A29-A31 / A33-A34）
# 2026-09-23 aw-codegen 按 docs/Swan回归用例AW实现方案.md §2.3 登记，
# PNG 由 aw-element 按 docs/agents/swan/aw-element.md 流程截取。
# 2026-09-24 aw-verify 真机实测（HONOR AKFDCP4718425500，720x1612）：底部
# 导航 4 图标存在+click 全通过、勾选态/收藏按钮 score=1.00@0.8
# （explorer_output/verify_regression1/），5 张 promote_image 转正，
# draft=True 改正式路径。搜索域 A33/A34 的 Tab 切换与结果断言用 OCR
# （Tab 行 region 限定），不需要新图。
# 仍留草稿（PNG 未截，需播放任务/授权平台）：
#    SWAN_PD_FAV_OFF / SWAN_PD_FAV_ON（歌单收藏两态）、
#    SWAN_PD_ROW_FAV_BTN（歌曲行收藏图标）。
# =====================================================================

# --- 底部导航 4 图标（A21；未选中态，与顶 Tab 5 张同口径；图标选中态不匹配未选中态模板） ---
SWAN_TAB_HOME = image_path("swan_底部导航_首页.png", platform="flutter")
SWAN_TAB_PLATFORM = image_path("swan_底部导航_平台.png", platform="flutter")
SWAN_TAB_DEVICE = image_path("swan_底部导航_设备.png", platform="flutter")
SWAN_TAB_ME = image_path("swan_底部导航_我的.png", platform="flutter")

# --- 歌单详情页 收藏图标两态（A29；只截图标本体，勿含歌单名/歌曲数文本） ---
SWAN_PD_FAV_OFF = image_path("swan_歌单详情页_收藏图标_未收藏.png", platform="flutter")
SWAN_PD_FAV_ON = image_path("swan_歌单详情页_收藏图标_已收藏.png", platform="flutter")

# --- 歌曲收藏入口（A30；⚠️ 2026-09-28 起 collect_song 停止引用下列三张，
# 5.3.2 实测口径见 knowledge/swan/draft/swan_收藏流程_532实测.md）---
# SWAN_PLAYER_FAV_BTN / SWAN_PLAYER_FAV_ON：5.3.2 播放页红心=「我喜欢」
#    toggle（红/灰两态翻转，无弹层无跳转），不再承担「收藏到指定歌单」
#    入口职能；保留登记供红心 toggle 独立辅助方法（收藏域）未来取用。
SWAN_PLAYER_FAV_BTN = image_path("swan_播放页_收藏按钮.png", platform="flutter")       # [5.3.2 语义变更] 播放页红心未收藏态（=我喜欢 toggle）
# 播放页红心已收藏态；verify-big52 根因6：红心对灰心模板实测 score≈0.47
# 必失配，两态须分别探测；element 截图中，暂登记 draft 路径
SWAN_PLAYER_FAV_ON = image_path("swan_播放页_收藏按钮_已收藏.png", platform="flutter", draft=True)
# 5.3.1 行内图标裁剪（40x40，内容=方框加号）；5.3.2 行内同位图标已改为
# [+]（同设计方框加号），旧裁剪对 5.3.2 行内 [+] 实测 score≈0.34 失配，
# collect_song 已停止引用（行内 [+] 模板已交付登记为
# SWAN_SONG_ROW_PLUS_BTN，见下方「收起钮双模板」段）
SWAN_PD_ROW_FAV_BTN = image_path("swan_歌单详情页_歌曲行收藏图标.png", platform="flutter")  # [5.3.2 失配] 旧行内图标，已由行内 [+] 模板替换

# --- 歌曲收藏 5.3.2 链路（A30；2026-09-28 aw-element 按 5.3.2 实测 §7
# 附带清单截取，暂登记 draft 路径，verify 转正后改正式路径）---
# 播放页底部三钮行中间的 [+]（无 key 无 desc 仅图可达，收藏链路入口）。
# ⚠️ 旧单模板 SWAN_PLAYER_PLUS_BTN（88x63）下缘含「VIP歌曲只支持试听」
#    提示文字像素且背景依赖：自家浅底实测 0.793 已不达 0.8 阈值（run5
#    文件3 collect[player] 死亡帧）——2026-09-29 aw-element 补截四模板
#    （image_ai draft），业务改 _PLUS_TEMPLATES 链式匹配（glyph→浅→深→
#    彩→旧单末位兜底，见 SwanBusiness._find_plus_btn）；[+] 配色随背景
#    明度自适应（浅底灰 glyph/深底白 glyph），跨族最高 0.402 必须链式。
SWAN_PLAYER_PLUS_BTN = image_path("swan_播放页_加号收藏钮.png", platform="flutter")  # [退役末位兜底] 88x63 含 VIP 横幅残留
SWAN_PLAYER_PLUS_BTN_GLYPH = image_path("swan_播放页_加号收藏钮_glyph.png", platform="flutter", draft=True)  # 38x38 紧贴 glyph，浅族通吃含无任务白底
SWAN_PLAYER_PLUS_BTN_LIGHT = image_path("swan_播放页_加号收藏钮_浅底.png", platform="flutter", draft=True)   # 50x50
SWAN_PLAYER_PLUS_BTN_DARK = image_path("swan_播放页_加号收藏钮_深底.png", platform="flutter", draft=True)    # 50x50 深/彩族 0.997+
SWAN_PLAYER_PLUS_BTN_COLOR = image_path("swan_播放页_加号收藏钮_彩底.png", platform="flutter", draft=True)   # 50x50
# 「选择平台收藏」底部弹层（存在性判据；弹层无取消钮、back 键关闭，
# 平台行清单随歌曲来源变化，行定位走 OCR 不走图）
SWAN_COLLECT_PLATFORM_SHEET = image_path("swan_收藏平台弹层.png", platform="flutter")
# 「已选N首歌」页顶栏（=KB 旧「选择歌单页」，标题含动态 N——[+] 单首
# 相加恒为 1；若裁剪含 N 数字，跨 N 场景需复核裁剪）
SWAN_COLLECT_SELECTED_TOPBAR = image_path("swan_已选歌曲顶栏.png", platform="flutter")


# =====================================================================
# Swan (Flutter) 收起钮双模板 / 音量滑条双模板 / 歌曲行内 [+]
# 2026-09-28 aw-element 按 run4c/run4d 复盘清单交付，暂登记 draft 路径，
# verify 转正后改正式路径。
# =====================================================================

# --- 播放页收起钮 浅底/深底双模板（run4c teardown 误点根因修复）---
# run4c 实测旧单模板 SWAN_PLAYER_DISMISS_BTN（浅青背景态）跨背景失配
# （播放中深色封面背景 score≈0.379），且与歌单详情页返回箭头同形互扰
# （对返回箭头 score 0.997 → teardown 在歌单详情页误点返回）。双模板按
# 背景极性分截（浅底/深底），实测极性 -0.9 根除互扰；探测另加顶栏
# region（y<200）双保险（见 SwanBusiness._find_dismiss_btn）。
# SWAN_PLAYER_DISMISS_BTN 保留登记作第三兜底（_find_dismiss_btn 探测链
# 仍在引用，勿删登记）。
SWAN_PLAYER_DISMISS_LIGHT = image_path("swan_播放页_收起按钮_浅底.png", platform="flutter", draft=True)
SWAN_PLAYER_DISMISS_DARK = image_path("swan_播放页_收起按钮_深底.png", platform="flutter", draft=True)

# --- 音量滑条 中填充态互补模板 ---
# ⚠️ 已废弃（2026-09-28 run4d run2 实测）：中填充图匹配矩形随音量态水平
# 漂移（同一轨道 x0=227/248/269/293），作几何锚比例换算必错（拖 40 实得
# 70）；纯轨道图对 69% 填充态 score 0.712 同样不可靠。set_volume 滑条定位
# 已改 ± 钮静态锚定推真轨道（见 SwanBusiness._find_volume_slider），两图
# 留档不引用。
SWAN_PLAYER_VOLUME_SLIDER_MID = image_path("swan_播放页_音量滑条_中填充.png", platform="flutter", draft=True)

# --- 歌单详情页/我喜欢页 歌曲行内 [+]（collect_song source="playlist_page"）---
# 5.3.2 行内 [+] 实测 bounds (616,796)-(688,868)@720 宽；element 实测
# 对同排垃圾桶区 score 0.268 无误触（垃圾桶与 [+] 中心相距 88px）、对
# 播放页 [+] score 0.372 无互扰。_tap_song_row_plus 改模板优先图定位
# （目标行 cy±40px 条带 region），_SONG_ROW_PLUS_TAP_X 保留作模板未命中
# 时的 OCR 行锚兜底。
SWAN_SONG_ROW_PLUS_BTN = image_path("swan_歌单详情页_歌曲行加号.png", platform="flutter", draft=True)


# =====================================================================
# Swan (Flutter) 设备钮变体 / 收起钮返回态 / 设备页本机分区锚点
# 2026-09-29 aw-element 按 A3（设备切换实弹）/B6（本机卡定位复测）
# 复盘清单交付，暂登记 draft 路径，verify 转正后改正式路径。
# =====================================================================

# --- 播放页设备切换钮 背景极性变体（A3 实弹：glyph 极性随背景亮度自适应）---
# 正式图 SWAN_PLAYER_DEVICE_BTN（浅底黑 glyph）只覆盖浅背景；rig 深色/
# 彩色封面背景失配（_switch_output_in_sheet 开弹层入口 rig 态失败根因）。
# GLYPH=白 glyph 裁剪（暗/彩底通吃，element 实测绿/黄底均 0.96+），
# GREEN=绿底整钮（兜底）。探测顺序 = 正式图 → GLYPH → GREEN，
# 见 SwanBusiness._find_device_btn。
SWAN_PLAYER_DEVICE_BTN_GLYPH = image_path("swan_播放页_设备切换钮_glyph.png", platform="flutter", draft=True)
SWAN_PLAYER_DEVICE_BTN_GREEN = image_path("swan_播放页_设备切换钮_绿底.png", platform="flutter", draft=True)

# --- 播放页收起钮 返回箭头态（白 chevron 深底；A3 开+收全流程实弹验证）---
# ⚠️ 与歌单详情页返回箭头同形，只准经 _find_dismiss_btn 模板组使用
# （组内统一 _PLAYER_TOPBAR_REGION region 限定，勿裸 find_image/click_image）。
SWAN_PLAYER_DISMISS_RETURN = image_path("swan_播放页_收起按钮_返回箭头态.png", platform="flutter", draft=True)

# --- 设备页 本机分区锚点（B6 新双栏布局）---
# 左栏「本机」分类 tab 选中/未选中两态 + 右栏「扬声器」节头标签（element
# 实测 cy≈357、bbox (185,339)-(280,369)；节头点击无效，卡体=节头 cy+140，
# 见 SwanBusiness._tap_local_speaker_card）。业务暂走实时 OCR（动态适配），
# 三图登记备用（OCR 失真时的图定位备选）。
SWAN_DEVICE_TAB_LOCAL_SEL = image_path("swan_设备页_本机tab_选中态.png", platform="flutter", draft=True)
SWAN_DEVICE_TAB_LOCAL_UNSEL = image_path("swan_设备页_本机tab_未选中态.png", platform="flutter", draft=True)
SWAN_DEVICE_SPEAKER_HEADER = image_path("swan_设备页_扬声器节头.png", platform="flutter", draft=True)


# =====================================================================
# Swan (Flutter) 回归第三轮修复·首页顶 Tab 选中态锚点（verify R2）
# 2026-09-24 aw-codegen 按 aw-verify 第二轮报告登记，PNG 由 aw-element
# 并行截取（A 组 5 张新名）。go_top_tab 到位断言统一换锚为「目标 Tab
# 选中态」图：切换后断言该 Tab 处于选中态，不再依赖各 Tab 内容布局
# （新构建音乐 Tab 改歌单流后原「音乐搜索条」内容锚点已失效），选中态
# 高亮样式跨机也更稳健。verify 转正后本段 draft=True 改正式路径。
# =====================================================================

# --- 首页顶 Tab 选中态（go_top_tab 到位锚点；截选中态高亮样式，勿含邻 Tab 与内容区） ---
SWAN_HOME_TAB_RECOMMEND_SEL = image_path("swan_首页_推荐Tab选中态.png", platform="flutter")
SWAN_HOME_TAB_MUSIC_SEL = image_path("swan_首页_音乐Tab选中态.png", platform="flutter")
SWAN_HOME_TAB_RADIO_SEL = image_path("swan_首页_电台Tab选中态.png", platform="flutter")
SWAN_HOME_TAB_AI_SEL = image_path("swan_首页_AITab选中态.png", platform="flutter")
SWAN_HOME_TAB_VISION_SEL = image_path("swan_首页_可视音箱Tab选中态.png", platform="flutter")



# =====================================================================
# W1-A 登录域 key 迁移用图（2026-10-12 真机命中已转正；SWAN_PWD_LOGIN_SUBMIT_ENABLED 暂挂——密码提交走 OCR，待密码域用例验证后转正）
# 截图日期：2026-10-12 | 设备：HONOR AKFDCP4718425500（720x1612）
# 用途：存量 accessibility key（login_* / me_user_profile_entry /
# person_info_logout_button）迁移为图像模板；verify 通过后
# promote_image 转正，draft=True 改正式路径。
# [2026-10-12 verify 验收] 8 图全部暂挂：均未被 W1-A 首批 7 用例
# （底部Tab轮巡/首页/平台页/设备页只读、播放页开关、收藏分组详情、搜索）
# 代码路径引用（静态零引用），且登录/密码域用例因 189 登录态保护禁跑；
# 全部维持 draft，待登录域/密码域用例批次真机命中后转正。
# =====================================================================

# --- 登录页（验证码形态，登出后落地页） ---
SWAN_LOGIN_PHONE_FIELD = image_path("swan_登录_手机号输入框.png", platform="flutter", )  # 页面=登录页 | 元素=手机号输入框未聚焦空态（整行白盒含边框，+86 段入模点击中心落号段）| 2026-10-12 | HONOR AKFDCP4718425500 720x1612 | 570x94
SWAN_LOGIN_AGREEMENT_UNCHECKED = image_path("swan_登录_协议勾选框_未选.png", platform="flutter", )  # 页面=登录页 | 元素=协议勾选框未选态（灰环本体不含文字，与已选态成对）| 2026-10-12 | HONOR AKFDCP4718425500 720x1612 | 30x30
SWAN_LOGIN_AGREEMENT_CHECKED = image_path("swan_登录_协议勾选框_已选.png", platform="flutter", )  # 页面=登录页 | 元素=协议勾选框已选态（黑底白勾，与未选态成对同位 30x30）| 2026-10-12 | HONOR AKFDCP4718425500 720x1612 | 30x30
SWAN_LOGIN_SUBMIT_ENABLED = image_path("swan_登录_下一步按钮_可用态.png", platform="flutter", )  # 页面=登录页 | 元素=「下一步」可用态黑底白字（已输号+已勾协议；与既有 SWAN_LOGIN_SUBMIT_BTN 置灰态成对，⛔ 勿点击提交）| 2026-10-12 | HONOR AKFDCP4718425500 720x1612 | 570x94
SWAN_LOGIN_PASSWORD_ENTRY = image_path("swan_登录_密码登入入口.png", platform="flutter", )  # 页面=登录页 | 元素=右上角「密码登入」切换入口（切密码登入页）| 2026-10-12 | HONOR AKFDCP4718425500 720x1612 | 132x34

# --- 密码登入页（与验证码页同根 login_page，右上角互切） ---
SWAN_PASSWORD_FIELD = image_path("swan_密码页_密码输入框.png", platform="flutter", )  # 页面=密码登入页 | 元素=密码输入框未聚焦空态（整行白盒含边框，右侧闭眼图标入模）| 2026-10-12 | HONOR AKFDCP4718425500 720x1612 | 582x94

# --- 我的页（logout 路径第一步，⚠️ 只截图/断言） ---
SWAN_ME_ACCOUNT_ENTRY = image_path("swan_我的_账号信息入口.png", platform="flutter", )  # 页面=我的页 | 元素=顶部账号信息入口行头像本体（结构性元素，不含昵称/手机号等个人数据；⚠️ 元素超浅色 std≈7，匹配阈值验收留意）| 2026-10-12 | HONOR AKFDCP4718425500 720x1612 | 122x122

# --- 个人信息页（⚠️ 上方「注销账号」为危险操作，其相邻区域严禁入模点击） ---
SWAN_PERSON_LOGOUT_BTN = image_path("swan_个人信息_退出登入按钮.png", platform="flutter", )  # 页面=个人信息页 | 元素=「退出登入」按钮文本（白底黑字；logout 清理路径终点）| 2026-10-12 | HONOR AKFDCP4718425500 720x1612 | 134x37
# 以下 2 张 2026-10-12 晚间补截（orchestrator 借四件套后未登录窗口，密码页填假表单态截图、未提交）：
SWAN_PWD_SMS_TOGGLE = image_path("swan_密码页_验证码登入入口.png", platform="flutter", )  # 页面=密码登入页 | 元素=右上角「验证码登入」回切钮（黑字态，填表后渲染）| 2026-10-12 | HONOR 720x1612 | 178x46
SWAN_PWD_LOGIN_SUBMIT_ENABLED = image_path("swan_密码页_登录按钮_可用态.png", platform="flutter", draft=True)  # 页面=密码登入页 | 元素=「登录」提交按钮黑底白字可用态（填表+勾协议后）| 2026-10-12 | HONOR 720x1612 | 220x78 | ⚠️ 2026-10-13 起「登录」提交走 [OCR] region 主路径（见 swan._LOGIN_SUBMIT_REGION），本图转备查不转正（黑底大按钮与置灰「下一步」模板存在形似互扰风险）
SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED = image_path("swan_平台_网易云音乐行_未授权态.png", platform="flutter", )  # 页面=平台页 | 元素=网易云音乐行卡未授权态（白底+「未授权」+黑[+]，logo+文字区不含[+]钮）| 2026-10-12 | HONOR 720x1612 | 400x124
SWAN_NETEASE_PLUS_BTN = image_path("swan_平台_网易云授权加号钮_未授权.png", platform="flutter", draft=True)  # 页面=平台页 | 元素=网易云行右侧黑色[+]授权钮（未授权态；A24 authorize_platform 操作目标 ⛔ 授权需专卡）| 2026-10-12 | HONOR 720x1612 | 60x58


__all__ = [
    "ANDROID_DRAFT_IMAGE_DIR",
    "ANDROID_IMAGE_DIR",
    "FLUTTER_DRAFT_IMAGE_DIR",
    "FLUTTER_IMAGE_DIR",
    "CURRENT_PLATFORM",
    "DRAFT_IMAGE_ROOT",
    "FORMAL_IMAGE_ROOT",
    "SUPPORTED_PLATFORMS",
    "SWAN_BOTTOM_PLAYER_BAR",
    "SWAN_DEVICE_ADD_BTN",
    "SWAN_FAV_ADD_PLAYLIST_BUTTON",
    "SWAN_FAV_FAMILY_GROUP_ROW",
    "SWAN_FAV_MUSIC_GROUP_ROW",
    "SWAN_FAMILY_ADD_MEMBER_ICON",
    "SWAN_LOGIN_CODE_FIELD_BOX",
    "SWAN_LOGIN_PRIVACY_POLICY_LINK",
    "SWAN_LOGIN_SUBMIT_BTN",
    "SWAN_LOGIN_USAGE_POLICY_LINK",
    "SWAN_ME_DEVICE_MANAGE_ROW",
    "SWAN_ME_FAMILY_MANAGE_ROW",
    "SWAN_ME_FAVORITES_ROW",
    "SWAN_ME_SOUND_QUALITY_ROW",
    "SWAN_PLATFORM_NETEASE_ROW",
    "SWAN_PLAYER_DISMISS_BTN",
    "SWAN_PLAYER_DISMISS_DARK",
    "SWAN_PLAYER_DISMISS_LIGHT",
    "SWAN_PLAYER_DISMISS_RETURN",
    "SWAN_PLAYER_PLAY_PAUSE_BTN",
    "SWAN_SOUND_QUALITY_DONE_BUTTON",
    "SWAN_HOME_TAB_RECOMMEND",
    "SWAN_HOME_TAB_MUSIC",
    "SWAN_HOME_TAB_RADIO",
    "SWAN_HOME_TAB_AI",
    "SWAN_HOME_TAB_VISION",
    "SWAN_HOME_TAB_RECOMMEND_SEL",
    "SWAN_HOME_TAB_MUSIC_SEL",
    "SWAN_HOME_TAB_RADIO_SEL",
    "SWAN_HOME_TAB_AI_SEL",
    "SWAN_HOME_TAB_VISION_SEL",
    "SWAN_HOME_MUSIC_SEARCH_BAR",
    "SWAN_HOME_RADIO_SEARCH_BAR",
    "SWAN_HOME_AI_ADD_ROLE",
    "SWAN_HOME_AI_ROLE_SETTINGS",
    "SWAN_HOME_VISION_UNBOUND_HINT",
    "SWAN_ME_SCAN_ICON",
    "SWAN_PROFILE_EDIT_DONE",
    "SWAN_PROFILE_EDIT_AVATAR_CANCEL",
    "SWAN_AREA_CODE_CHINA_ROW",
    "SWAN_PLAYLIST_BACK_BTN",
    "SWAN_PLAYLIST_CREATE_BTN",
    "SWAN_PLAYLIST_TAB_SWAN",
    "SWAN_PLAYLIST_NEWDLG_CLOSE_BTN",
    "SWAN_PD_MORE_BTN",
    "SWAN_PD_PLAY_ALL",
    "SWAN_FAVORITE_PLAY_ALL",
    "SWAN_HISTORY_TOPBAR",
    "SWAN_HISTORY_TABBAR",
    "SWAN_DEVICE_SHEET_TITLE",
    "SWAN_PLAYER_DEVICE_BTN",
    "SWAN_PLAYER_DEVICE_BTN_GLYPH",
    "SWAN_PLAYER_DEVICE_BTN_GREEN",
    "SWAN_AI_CHAT_VOICE_BTN",
    "SWAN_AI_CHAT_INPUT",
    "SWAN_SEARCH_BACK",
    "SWAN_SEARCH_SUBMIT",
    "SWAN_SEARCH_CLEAR",
    "SWAN_SEARCH_EMPTY",
    "SWAN_AUTH_GATE_LOGIN_BTN",
    "SWAN_AUTH_GATE_ADD_BTN",
    "SWAN_PLATFORM_RADIO_ROW_ARROW",
    "SWAN_ALL_ROLES_MULTISELECT",
    "SWAN_ROLE_EDITOR_SELECT",
    "SWAN_ROLE_EDITOR_MORE_PLATFORM",
    "SWAN_ROLE_EDITOR_DONE",
    "SWAN_ROLE_IMAGES_DIY_BTN",
    "SWAN_DIY_GENERATE_BTN",
    "SWAN_DIY_UPLOAD_CARD",
    "SWAN_AI_PLATFORM_ROW_BTN",
    "SWAN_AI_PLATFORM_TITLE",
    "SWAN_AI_HISTORY_TITLE",
    "SWAN_PLAYER_PAUSE_BTN",
    "SWAN_PLAYER_PREV_BTN",
    "SWAN_PLAYER_NEXT_BTN",
    "SWAN_PLAYER_LOOP_LIST",
    "SWAN_PLAYER_LOOP_SINGLE",
    "SWAN_PLAYER_LOOP_SHUFFLE",
    "SWAN_PLAYER_PROGRESS_BAR",
    "SWAN_PLAYER_VOLUME_ICON",
    "SWAN_PLAYER_VOLUME_ICON_GLYPH",
    "SWAN_PLAYER_VOLUME_ICON_LIGHT",
    "SWAN_PLAYER_VOLUME_ICON_DARK",
    "SWAN_PLAYER_VOLUME_POPUP",
    "SWAN_PLAYER_VOLUME_SLIDER",
    "SWAN_PLAYER_VOLUME_SLIDER_MID",
    "SWAN_PLAYER_VOLUME_PLUS",
    "SWAN_PLAYER_VOLUME_MINUS",
    "SWAN_DEVICE_CARD_SELECTED",
    "SWAN_DEVICE_SHEET_CHECKED",
    "SWAN_DEVICE_SPEAKER_HEADER",
    "SWAN_DEVICE_TAB_LOCAL_SEL",
    "SWAN_DEVICE_TAB_LOCAL_UNSEL",
    "SWAN_BOTTOM_BAR_CAST_BTN",
    "SWAN_TAB_HOME",
    "SWAN_TAB_PLATFORM",
    "SWAN_TAB_DEVICE",
    "SWAN_TAB_ME",
    "SWAN_PD_FAV_OFF",
    "SWAN_PD_FAV_ON",
    "SWAN_PLAYER_FAV_BTN",
    "SWAN_PLAYER_FAV_ON",
    "SWAN_PD_ROW_FAV_BTN",
    "SWAN_SONG_ROW_PLUS_BTN",
    "SWAN_PLAYER_PLUS_BTN",
    "SWAN_PLAYER_PLUS_BTN_GLYPH",
    "SWAN_PLAYER_PLUS_BTN_LIGHT",
    "SWAN_PLAYER_PLUS_BTN_DARK",
    "SWAN_PLAYER_PLUS_BTN_COLOR",
    "SWAN_COLLECT_PLATFORM_SHEET",
    "SWAN_COLLECT_SELECTED_TOPBAR",
    "SWAN_LOGIN_PHONE_FIELD",
    "SWAN_LOGIN_AGREEMENT_UNCHECKED",
    "SWAN_LOGIN_AGREEMENT_CHECKED",
    "SWAN_LOGIN_SUBMIT_ENABLED",
    "SWAN_LOGIN_PASSWORD_ENTRY",
    "SWAN_PASSWORD_FIELD",
    "SWAN_ME_ACCOUNT_ENTRY",
    "SWAN_PERSON_LOGOUT_BTN",
    "SWAN_PWD_SMS_TOGGLE",
    "SWAN_PWD_LOGIN_SUBMIT_ENABLED",
    "SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED",
    "SWAN_NETEASE_PLUS_BTN",
    "WEB_DRAFT_IMAGE_DIR",
    "WEB_IMAGE_DIR",
    "demote_image",
    "get_image_dir",
    "image_path",
    "normalize_platform",
    "path",
    "promote_image",
    "test_path",
]
