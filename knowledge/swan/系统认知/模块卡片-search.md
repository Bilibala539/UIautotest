# 模块卡片：module-17-search

## 基线与范围

- 数据标签：`TEST-SYNTHETIC`；任务：`SWAN-20260904-003-search-archaeology`；角色：`archaeologist`。
- App 仓库：`E:\SwanApp\repos\flutter\HiVi-Network-FlutterApp`，`dev@4d1ed7b1d727f12906d6ac9fa9ed195966e464b3`。
- Core 仓库：`E:\SwanApp\repos\flutter\hivi_network_flutter_core`，`dev@402853ab964f026761ba63130f495b9d213ea8b5`。
- App 通过 `pubspec.yaml` 的相对路径 `../hivi_network_flutter_core` 依赖 Core；两仓库均已有 `analysis_options.yaml`、`pubspec.lock` 未提交改动，本任务未修改。
- 执行模式：只读考古；未执行测试、未设计正向/负向/对抗用例，未修改业务源、测试、依赖、配置，未提交或推送。

## 入口与可达路由

应用启动由 App `lib/main.dart`（解析默认运行平台后 `AppBootstrap.run(pureFlutterStandalone: true)`）或 `lib/main_ohos.dart`（显式 OHOS）进入 Core bootstrap。`AppBootstrap` 注册 `Provider<SearchPort>`，默认实现为 `PureFlutterSearchPort`。

搜索入口调用方（均最终到 `AppRouter.searchEntry`，Qobuz 另使用别名 `AppRouter.search`）：

1. 推荐页：`pure_flutter_recommend_page_port.dart:65-80`，平台 `all`。
2. 首页音乐 Tab：`home_music_page.dart:180-189`，平台 `all`、首个歌曲 Tab、Hero tag。
3. 首页电台 Tab：`home_radio_page.dart:193-203`，平台 `all`、电台 Tab（index 4）。
4. 平台内容页：`platform_content_page.dart:227-234`，平台由 `PlatformContentKind` 映射，携带平台内容 Hero tag。
5. Qobuz 首页：`qobuz_home_page.dart:317-329`，平台 `qobuz`，路由别名 `search`。
6. 全国电台详情：`fm_country_radio_page.dart:74-85`，电台 Tab、`stationTerraceType: '0'`。
7. 80/90 电台详情：`fm_harmony_radio_page.dart:64-77`，电台 Tab、`stationTerraceType` 为 `'6'` 或 `'5'`。
8. Apple Music Port：`pure_flutter_apple_music_port.dart:100-113`，平台 `appleMusic`。

路由解析：`AppRouter.search`=`/main/search` 与 `AppRouter.searchEntry`=`/search` 都构建 `SearchPage`；`AppRouter.searchResults`=`/search/results` 构建 `SearchResultsPage`（`pure_flutter_router.dart:781-787`）。搜索结果路由在底部播放器集合中（`pure_flutter_router.dart:376-423`，其中 `searchResults` 在 406 行）；输入页不加入该集合，结果页可播放。

## 页面、控制器与数据流

- `SearchPage`（`presentation/pages/search/search_page.dart`）维护 keyword、平台、当前 Tab、历史态和键盘/RouteAware 焦点策略。提交时 trim、写历史、切换结果态并刷新历史（`203-220`）；清空历史走 `SearchPort`（`222-233`）。
- `SearchResultsContent` 固定原生顺序 song/artist/album/playlist/station/podcast，使用 `PageView` + `AutomaticKeepAliveClientMixin`，仅活动 Tab 首次请求；keyword/platform/station terraceType 变化通过 key 丢弃旧缓存（`search_results_content.dart:42-127,136-245`）。
- 结果列表按 `SecondaryMusicGroup` 分组，默认每组显示 5 条，可展开；点击统一交给 `SearchResultActionAdapter`（`search_results_content.dart:256-365`）。
- `SearchResultsPage` 是深链壳，复用 `SearchResultsContent`（`search_results_page.dart:12-40`）。

## 接口、仓储与模型

- Port：`core/platform_ports/search_port.dart:8-27` 定义历史 CRUD、热门搜索和 `search(keyword, platform, category, page)`。
- 默认适配器：`data/services/pure_flutter_search_port.dart:13-97`；历史 key=`search_history`，最多 20 条，依赖 `KeyValueStorage`；热门搜索当前为静态列表；搜索先追加历史，再委托 HTTP 服务。
- HTTP/API：`MusicSecondaryHttpService.search` 调用 `AuthApi.get(AppConstants.baseUrl, 'music/search')`，参数 `type/keyword/numType/terraceType`（`music_secondary_http_service.dart:27-90`）。
- 分类到 API：artist→type 12、album→8、playlist→20、station→15、podcast→25、song/mixed/mv→0；平台 terraceType：QQ 1、网易 3、酷狗 4、Apple 19、Qobuz 22、all 0（`music_secondary_http_service.dart:912-960`）。
- 模型：`SearchCategory` 保留旧值并由 UI 显式映射原生六 Tab（`secondary_page_models.dart:474-489`）；`SecondaryMusicGroup` 携带 title/items/platform/terraceType/raw；`SearchResultsSnapshot` 保存各类列表、视频和分组（`secondary_page_models.dart:491-553`）。
- 解析边界：服务兼容 `data` 列表、分组 `name/title/terraceType/list` 和平铺列表；item id/title/cover 支持多平台字段别名，优先 group terraceType，空组过滤（`music_secondary_http_service.dart:389-506,508-648`）。
- 结果动作：歌曲/电台通过 `UnifiedMusicPort` 播放，艺人/歌单/专辑/播客导航到 `artistDetail` 或 `playlistDetail`；Apple MV 在 Android `Platform.isAndroid` 下提示不支持；Apple 播客直接播放，Qobuz 播客按专辑详情处理（`search_result_action_adapter.dart:32-74,194-218,271-338`）。

## 平台分支、开关与依赖

- 运行平台分支：App `main.dart` 使用 `AppRuntimePlatform.resolveDefault()`；OHOS 使用显式 `AppRuntimePlatform.ohos`（`main.dart:8-18`、`main_ohos.dart:7-17`）。
- Core Provider 注入：`app_bootstrap.dart:921-929`。无发现专用 feature flag；行为由 `UnifiedMusicPlatform`、`SearchCategory`、`stationTerraceType` 和运行平台分支决定。
- 关键包依赖：Flutter、`provider`、`dio`、`shared_preferences`/`path_provider`（存储实现）、`cached_network_image`、`lottie`；Core `pubspec.yaml` 还声明多平台音频/平台 SDK 包。

## 已知坑点与 QA 边界

- 空 keyword 直接返回空快照，不发请求；历史 trim、去重并最多保留 20 条。
- 全平台或电台搜索抑制全局授权提示；单平台搜索保留授权提示（`music_secondary_http_service.dart:33-64`）。
- 后端异常在结果页被收敛为空态（`search_results_content.dart:229-244`），不能仅凭“空列表”判断无数据。
- 内联搜索页与深链结果页共享组件但底部播放器策略不同；结果页在 `_bottomPlayerRouteNames`，输入页不在。
- PageView 仅活动 Tab 首次加载并 keep-alive；切换 keyword/platform/电台分组过滤时会重建缓存。
- 电台详情传入 `stationTerraceType` 后仅保留匹配分组；全国=`0`、90s=`5`、80er=`6`。未传时首页电台搜索保留全部 FM 分组。
- 解析字段高度多态：QQ/网易歌单 id 可能是 `dissid/docid/diss_id`；Qobuz 播客常用 `album_id/album_name/album_pic`。
- 搜索结果动作包含 Android-only Apple MV 不支持分支，且平台/播客点击语义不同；后续检查需按 `terraceType` 分支取证。

## 证据索引

逐条源码位置、符号和观察结论见任务结果目录：`F:\SwanApp-Toolchain\results\SWAN-20260904-003-search-archaeology\evidence\source-location-index.md`。
