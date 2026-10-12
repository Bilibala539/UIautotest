# -*- coding: utf-8 -*-
"""在《回归用例.xlsx》新增「自动化映射」sheet：76 条文字用例 → 自动化文件/方法/AW 映射。"""
import openpyxl

XLSX = r'C:\Users\menglz.SWANSPEAKERS\Desktop\回归用例_自动化映射.xlsx'
SOURCE = r'C:\Users\menglz.SWANSPEAKERS\Desktop\回归用例.xlsx'

rows = [
    ["用例编号", "模块", "用例标题", "自动化文件(tests/flutter/)", "自动化用例方法", "AW方法(SwanBusiness/Base)", "自动化状态", "真机验证", "说明"],
    # 启动合规与登录认证 1-8
    [1, "启动合规与登录认证", "首次安装后冷启动", "test_验证码登录.py（存量拆分）", "存量登录用例组", "login/relaunch_app", "存量覆盖", "部分", "改造项:登录域key定位→图/OCR(批次待排)"],
    [2, "启动合规与登录认证", "登录后的冷启动", "test_验证码登录.py（存量拆分）", "存量登录用例组", "login", "存量覆盖", "部分", "同上"],
    [3, "启动合规与登录认证", "热启动APP", "—", "—", "background_resume", "未实现", "—", "批次待排"],
    [4, "启动合规与登录认证", "手机号验证码登录", "test_启动合规与登录认证.py（计划）", "—", "login_by_sms(已实证OTP自愈)", "未实现", "—", "域1改造批次"],
    [5, "启动合规与登录认证", "手机号密码登录", "test_密码登录成功.py（存量拆分）", "test_password_login", "login_with_password", "存量覆盖", "部分", "key定位,待改造"],
    [6, "启动合规与登录认证", "微信登录", "—", "—", "login_by_wechat", "未实现", "—", "跨App,批次待排"],
    [7, "启动合规与登录认证", "微博登录", "—", "—", "login_by_weibo", "未实现", "—", "跨App,批次待排"],
    [8, "启动合规与登录认证", "请绑定手机页回退", "—", "—", "bind_phone_back", "未实现", "—", "批次待排"],
    # 配网 9-10
    [9, "配网", "蓝牙配网", "—", "—", "provision_by_ble", "未实现", "—", "等D1真机验证+未配网设备"],
    [10, "配网", "热点配网", "—", "—", "provision_by_hotspot", "未实现", "—", "D1 connect_wifi已实现未验证"],
    # 播放器与播放控制 11-28
    [11, "播放器与播放控制", "设备界面播放器切换设备", "test_播放器设备切换.py", "test_switch_device_from_device_page_card", "select_device(via=card,双栏重写)", "已实现", "绿", ""],
    [12, "播放器与播放控制", "播放条切换设备", "test_播放器设备切换.py", "test_switch_device_from_player_sheet", "select_device(via=player)", "已实现", "绿", ""],
    [13, "播放器与播放控制", "扬声器播放", "test_播放器播放控制.py", "test_play_all_from_favorite[speaker]", "start_play+assert_playing", "已实现", "绿", ""],
    [14, "播放器与播放控制", "设备播放", "test_播放器播放控制.py", "test_play_all_from_favorite[wifi]", "start_play(wifi)", "已实现", "绿", "音箱在线窗口验证"],
    [15, "播放器与播放控制", "播放循环模式切换", "test_播放器播放控制.py", "test_loop_mode_and_controls[*/list]", "set_loop_mode+player_control", "已实现", "绿", ""],
    [16, "播放器与播放控制", "扬声器列表循环播放控制", "test_播放器播放控制.py", "test_loop_mode_and_controls[speaker-list]", "player_control+assert_playing/paused", "已实现", "绿", ""],
    [17, "播放器与播放控制", "扬声器单曲循环播放控制", "test_播放器播放控制.py", "test_loop_mode_and_controls[speaker-single]", "player_control+set_loop_mode", "已实现", "绿", ""],
    [18, "播放器与播放控制", "扬声器随机播放播放控制", "test_播放器播放控制.py", "test_loop_mode_and_controls[speaker-shuffle]", "player_control(瞬态flake观察)", "已实现", "flake", "红绿红三态观察项"],
    [19, "播放器与播放控制", "WIFI音响设备播放循环模式切换", "test_播放器播放控制.py", "test_loop_mode_and_controls[wifi-list]", "set_loop_mode(wifi)", "已实现", "绿", ""],
    [20, "播放器与播放控制", "WiFi音响设备列表循环播放控制", "test_播放器播放控制.py", "test_loop_mode_and_controls[wifi-list]", "player_control(wifi)", "已实现", "绿", ""],
    [21, "播放器与播放控制", "WiFi音响设备单曲循环播放控制", "test_播放器播放控制.py", "test_loop_mode_and_controls[wifi-single]", "player_control(wifi)", "已实现", "绿", ""],
    [22, "播放器与播放控制", "WiFi音响设备随机播放播放控制", "test_播放器播放控制.py", "test_loop_mode_and_controls[wifi-shuffle]", "player_control(wifi)", "已实现", "绿", ""],
    [23, "播放器与播放控制", "扬声器进度条控制", "test_播放器进度与音量.py", "test_seek_progress[speaker-drag/click]", "seek_to(drag/click)+OCR双时间", "已实现", "绿×2", ""],
    [24, "播放器与播放控制", "设备进度条控制", "test_播放器进度与音量.py", "test_seek_progress[wifi-*]", "seek_to(wifi)", "已实现", "绿", "音箱在线窗口验证"],
    [25, "播放器与播放控制", "扬声器音量弹窗音量控制", "test_播放器进度与音量.py", "test_volume_adjust[speaker-*]", "set_volume(drag/click/plus/minus)+断言双通道", "已实现", "绿×4", ""],
    [26, "播放器与播放控制", "设备音量弹窗音量控制", "test_播放器进度与音量.py", "test_volume_adjust[wifi-*]", "set_volume(wifi)", "已实现", "绿×4", "音箱在线窗口验证"],
    [27, "播放器与播放控制", "手机按键调整扬声器音量大小", "test_播放器进度与音量.py", "test_volume_key[speaker-*]", "volume_key+long_press_key", "已实现", "绿×3", ""],
    [28, "播放器与播放控制", "手机按键调整设备音量大小", "test_播放器进度与音量.py", "test_volume_key[wifi-*]", "volume_key(wifi)", "已实现", "绿", "音箱在线窗口验证"],
    # 导航 29-31
    [29, "主框架导航与首页推荐", "底部导航栏切换", "test_主框架导航与首页推荐.py", "test_bottom_tab_switch[平台/设备/首页/我的]", "go_bottom_tab", "已实现", "绿×4", ""],
    [30, "主框架导航与首页推荐", "首页顶部导航栏切换", "test_主框架导航与首页推荐.py", "test_top_tab_switch[音乐/AI/可视音箱/电台/推荐]", "go_top_tab(选中态锚)", "已实现", "绿×5", ""],
    [31, "主框架导航与首页推荐", "推荐页功能", "test_主框架导航与首页推荐.py", "test_home_card_entry[我喜欢/歌单/AI/最近播放]", "open_home_card", "已实现", "绿", ""],
    # 平台授权 32-37
    [32, "音乐平台总览与授权", "QQ音乐授权", "—", "—", "authorize_platform(qq)", "未实现", "—", "等音箱窗口批次"],
    [33, "音乐平台总览与授权", "网易云音乐授权", "—", "—", "authorize_platform(netease)", "未实现", "—", "同上"],
    [34, "音乐平台总览与授权", "酷狗音乐授权", "—", "—", "authorize_platform(kugou)", "未实现", "—", "同上"],
    [35, "音乐平台总览与授权", "首页QQ音乐授权", "—", "—", "authorize_platform(qq,entry=home)", "未实现", "—", "同上"],
    [36, "音乐平台总览与授权", "首页网易云音乐授权", "—", "—", "authorize_platform(netease,entry=home)", "未实现", "—", "同上"],
    [37, "音乐平台总览与授权", "首页酷狗音乐授权", "—", "—", "authorize_platform(kugou,entry=home)", "未实现", "—", "同上"],
    # 平台内容页 38-40
    [38, "平台内容页", "QQ音乐平台内容页", "—", "—", "open_platform+open_platform_entry", "未实现", "—", "等explorer补3平台主页draft"],
    [39, "平台内容页", "网易云音乐平台内容页", "—", "—", "open_platform+open_platform_entry", "未实现", "—", "同上"],
    [40, "平台内容页", "酷狗音乐平台内容页", "—", "—", "open_platform+open_platform_entry", "未实现", "—", "同上"],
    # 歌单收藏与历史 41-68
    [41, "歌单、收藏与历史", "QQ音乐歌单收藏", "test_歌单收藏与历史.py", "test_favorite_playlist_toggle_twice[swan]", "favorite_playlist", "已实现", "红(产品)", "5.3.2移除收藏图标载体,待产品决策"],
    [42, "歌单、收藏与历史", "网易云音乐歌单收藏", "同41", "同41", "favorite_playlist", "同41", "同41", "同上"],
    [43, "歌单、收藏与历史", "酷狗音乐歌单收藏", "同41", "同41", "favorite_playlist", "同41", "同41", "同上"],
    [44, "歌单、收藏与历史", "播放页QQ音乐歌曲收藏到QQ音乐中", "test_歌单收藏与历史.py", "test_collect_song[swan-player]", "collect_song(player,+→平台弹层→宫格)+预清理", "已实现", "绿", "预校验防重复收藏"],
    [45, "歌单、收藏与历史", "播放页网易云音乐歌曲收藏", "同44", "同44", "collect_song(player,netease)", "未实现", "—", "等平台授权+换源数据"],
    [46, "歌单、收藏与历史", "播放页酷狗音乐歌曲收藏", "同45", "同45", "collect_song(player,kugou)", "未实现", "—", "同上"],
    [47, "歌单、收藏与历史", "播放页QQ歌曲收藏到swan中", "同44", "同44", "collect_song(player,swan)", "未实现", "—", "同上"],
    [48, "歌单、收藏与历史", "播放页网易云歌曲收藏到swan中", "同45", "同45", "collect_song(player,swan,netease)", "未实现", "—", "同上"],
    [49, "歌单、收藏与历史", "播放页酷狗歌曲收藏到swan中", "同46", "同46", "collect_song(player,swan,kugou)", "未实现", "—", "同上"],
    [50, "歌单、收藏与历史", "歌单页收藏QQ音乐歌曲到QQ音乐歌单中", "test_歌单收藏与历史.py", "test_collect_song[swan-playlist_page]", "collect_song(playlist_page,行内[+]模板)", "已实现", "绿", "源歌单换SWAN_COLLECT_SOURCE_PLAYLIST"],
    [51, "歌单、收藏与历史", "歌单页收藏网易云音乐歌曲", "同50", "同50", "collect_song(playlist_page,netease)", "未实现", "—", "等平台授权"],
    [52, "歌单、收藏与历史", "歌单页收藏酷狗音乐歌曲", "同51", "同51", "collect_song(playlist_page,kugou)", "未实现", "—", "同上"],
    [53, "歌单、收藏与历史", "歌单页收藏QQ音乐歌曲到swan歌单中", "同50", "同50", "collect_song(playlist_page,swan)", "未实现", "—", "同上"],
    [54, "歌单、收藏与历史", "歌单页收藏网易云音乐歌曲到swan歌单中", "同51", "同51", "collect_song(playlist_page,swan,netease)", "未实现", "—", "同上"],
    [55, "歌单、收藏与历史", "歌单页收藏酷狗音乐歌曲到swan歌单中", "同52", "同52", "collect_song(playlist_page,swan,kugou)", "未实现", "—", "同上"],
    [56, "歌单、收藏与历史", "播放QQ音乐记录到最近播放中", "test_歌单收藏与历史.py", "test_recent_played[歌曲]", "start_play+assert_recent_played", "已实现", "绿×2", "条件造数:SWAN_HISTORY_FRESH_PLAY"],
    [57, "歌单、收藏与历史", "播放网易云音乐记录到最近播放中", "test_歌单收藏与历史.py", "test_recent_played[歌曲-netease]", "同上(需netease授权)", "未实现", "—", "等平台授权"],
    [58, "歌单、收藏与历史", "播放酷狗音乐记录到最近播放中", "—", "—", "同上(需kugou授权)", "未实现", "—", "同上"],
    [59, "歌单、收藏与历史", "播放QQ音乐歌单记录到最近播放中", "—", "—", "start_play(source=歌单)+assert_recent_played(歌单)", "未实现", "—", "批次待排"],
    [60, "歌单、收藏与历史", "播放网易云音乐歌单记录到最近播放中", "—", "—", "同上(需netease)", "未实现", "—", "同上"],
    [61, "歌单、收藏与历史", "播放酷狗音乐歌单记录到最近播放中", "—", "—", "同上(需kugou)", "未实现", "—", "同上"],
    [62, "歌单、收藏与历史", "记录已播的QQ音乐歌手", "—", "—", "播放歌手页条目+assert_recent_played(歌手)", "未实现", "—", "批次待排"],
    [63, "歌单、收藏与历史", "记录已播的网易云音乐歌手", "—", "—", "同上(需netease)", "未实现", "—", "同上"],
    [64, "歌单、收藏与历史", "记录已播的酷狗音乐歌手", "—", "—", "同上(需kugou)", "未实现", "—", "同上"],
    [65, "歌单、收藏与历史", "记录已播的博客数据", "—", "—", "播放博客+assert_recent_played(博客)", "未实现", "—", "批次待排"],
    [66, "歌单、收藏与历史", "记录已播放的电台", "—", "—", "播放电台+assert_recent_played(电台)", "未实现", "—", "批次待排"],
    [67, "歌单、收藏与历史", "手动切歌把歌曲记录到最近播放中", "—", "—", "player_control(next)+assert_recent_played", "未实现", "—", "批次待排"],
    [68, "歌单、收藏与历史", "自动切歌把歌曲记录到最近播放中", "—", "—", "等整曲播完(夜间跑)+assert_recent_played", "未实现", "—", "耗时极长,夜间批"],
    # 搜索 69-72
    [69, "搜索", "跨平台搜索", "test_搜索.py", "test_search_results_by_tab[×6tab×home]", "search+assert_search_results(双口径)", "已实现", "绿×5+1(电台空态allow_empty)", ""],
    [70, "搜索", "QQ音乐平台搜索", "test_搜索.py", "test_search_results_by_tab[×6tab×radio]", "search(entry=radio)", "已实现", "绿", ""],
    [71, "搜索", "网易云音乐平台搜索", "同70", "同70", "search(entry=radio)", "同70", "同70", ""],
    [72, "搜索", "酷狗音乐平台搜索", "同70", "同70", "search(entry=radio)", "同70", "同70", ""],
    # 设备列表与多房间 73-76
    [73, "设备列表与多房间", "A31设备同步播放一台设备", "—", "—", "sync_rooms+assert_room_synced", "未实现", "—", "等多台同芯片rig"],
    [74, "设备列表与多房间", "A31设备同步播放多台设备", "—", "—", "sync_rooms(多台)", "未实现", "—", "同上"],
    [75, "设备列表与多房间", "H76D/H76G设备同步播放一台设备", "—", "—", "sync_rooms(H76)", "未实现", "—", "同上"],
    [76, "设备列表与多房间", "H76D/H76G设备同步播放多台设备", "—", "—", "sync_rooms(多台)", "未实现", "—", "同上"],
]

wb = openpyxl.load_workbook(SOURCE)
if '自动化映射' in wb.sheetnames:
    del wb['自动化映射']
ws = wb.create_sheet('自动化映射')
for r in rows:
    ws.append(r)
# 表头加粗
from openpyxl.styles import Font
for cell in ws[1]:
    cell.font = Font(bold=True)
# 列宽
widths = [9, 20, 30, 34, 42, 42, 12, 12, 36]
from openpyxl.utils import get_column_letter
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = 'A2'
wb.save(XLSX)
print('saved:', XLSX, '映射行数:', len(rows) - 1)
