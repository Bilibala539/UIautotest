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
SWAN_PLAYER_PAUSE_BTN = image_path("swan_播放页_暂停按钮.png", platform="flutter", draft=True)       # 播放中的 ⏸ 态圆钮
SWAN_PLAYER_PREV_BTN = image_path("swan_播放页_上一首按钮.png", platform="flutter")
SWAN_PLAYER_NEXT_BTN = image_path("swan_播放页_下一首按钮.png", platform="flutter")
SWAN_PLAYER_LOOP_LIST = image_path("swan_播放页_循环模式_列表循环.png", platform="flutter")     # 循环钮三态之一
SWAN_PLAYER_LOOP_SINGLE = image_path("swan_播放页_循环模式_单曲循环.png", platform="flutter", draft=True)
SWAN_PLAYER_LOOP_SHUFFLE = image_path("swan_播放页_循环模式_随机播放.png", platform="flutter", draft=True)
SWAN_PLAYER_PROGRESS_BAR = image_path("swan_播放页_进度条.png", platform="flutter")    # 进度条整条（滑条锚；勿含两端时间文字）

# --- 播放页 音量弹窗 ---
SWAN_PLAYER_VOLUME_ICON = image_path("swan_播放页_音量图标.png", platform="flutter")   # 播放页底部音量入口图标
SWAN_PLAYER_VOLUME_POPUP = image_path("swan_播放页_音量弹窗.png", platform="flutter")  # 弹窗整体或标题区（存在性判据）
SWAN_PLAYER_VOLUME_SLIDER = image_path("swan_播放页_音量滑条.png", platform="flutter")  # 弹窗内滑条整条（拖动锚）
SWAN_PLAYER_VOLUME_PLUS = image_path("swan_播放页_音量加号按钮.png", platform="flutter")
SWAN_PLAYER_VOLUME_MINUS = image_path("swan_播放页_音量减号按钮.png", platform="flutter")

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
SWAN_PD_FAV_OFF = image_path("swan_歌单详情页_收藏图标_未收藏.png", platform="flutter", draft=True)
SWAN_PD_FAV_ON = image_path("swan_歌单详情页_收藏图标_已收藏.png", platform="flutter", draft=True)

# --- 歌曲收藏入口（A30） ---
SWAN_PLAYER_FAV_BTN = image_path("swan_播放页_收藏按钮.png", platform="flutter")       # 全屏播放页收藏入口（source="player"）
SWAN_PD_ROW_FAV_BTN = image_path("swan_歌单详情页_歌曲行收藏图标.png", platform="flutter", draft=True)  # 歌单详情页歌曲行收藏图标（source="playlist_page"）


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
    "SWAN_PLAYER_VOLUME_POPUP",
    "SWAN_PLAYER_VOLUME_SLIDER",
    "SWAN_PLAYER_VOLUME_PLUS",
    "SWAN_PLAYER_VOLUME_MINUS",
    "SWAN_DEVICE_CARD_SELECTED",
    "SWAN_DEVICE_SHEET_CHECKED",
    "SWAN_BOTTOM_BAR_CAST_BTN",
    "SWAN_TAB_HOME",
    "SWAN_TAB_PLATFORM",
    "SWAN_TAB_DEVICE",
    "SWAN_TAB_ME",
    "SWAN_PD_FAV_OFF",
    "SWAN_PD_FAV_ON",
    "SWAN_PLAYER_FAV_BTN",
    "SWAN_PD_ROW_FAV_BTN",
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
