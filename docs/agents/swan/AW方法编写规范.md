# Swan AW 方法编写规范（强制遵守）

> 适用：所有进入 `SwanBusiness`（utils/aw/business/swan.py）与回归 mixin（utils/aw/business/swan_regression.py）的方法。
> 本规范从既有最佳实现提炼（样板：`favorite_playlist` / `remove_song_from_playlist` / `assert_recent_played`，2026-10 定稿）。
> 配套：AW 方法指南（查已有方法防重复）· 测试用例文件规范（用例层）· CLAUDE.md 规则 1-10（硬约束）。

## 1. 方法签名

- **完整类型注解**：参数与返回值必须标注（`def favorite_playlist(self, platform: str, state: str = "on", timeout: float = 10.0) -> None:`）
- **参数命名用业务语义**：`platform / state / kind / via / source / action / mode`，禁 `a / b / flag / param1`
- **每个等待点显式 `timeout` 参数**并给默认值（默认值须有依据：瞬态窗口实测，如 20s 覆盖切歌 loading）
- **返回值约定（二分法）**：
  - **动作方法 → `None`**：失败就地 `assert` 死（消息带证据与排查方向），不返回 bool 让调用方猜
  - **查询方法 → 值**：找不到返回 `None`/`False`（如 `_playlist_fav_state() -> str | None`），**把断言权交给调用方**——查询方法自己不 assert

## 2. docstring 强制结构（六要素）

```python
def xxx(self, ...) -> None:
    """一句话功能（编号 Axx，回归用例 N-M）。          ← ① 身份

    前置/路由：复用哪个方法、短路语义（已在目标页时短路）。 ← ② 前置
    定位：收藏图标两态 [图]（域N 新截）；出口文本 [OCR]。   ← ③ 定位方式
    流程：A -> B -> C。                                  ← ④ 流程链
    收尾断言：目标态图标 [图]。                           ← ⑤ 断言口径
    ⚠️ 坑注记：收藏持久化在账号数据，回滚用两次 toggle。    ← ⑥ 坑与假设
    返回 False = 歌不在歌单内；后置条件 = 全局 tab 壳。     ← ⑦ 返回/后置（如有）
    """
```

- 编号沿回归方案 §2.3（Axx）；无编号的新方法写服务用例号或"通用前置"
- 定位方式**逐控件标注**：[图] / [OCR] / key（仅存量迁移期允许，注明"存量待迁移"）
- ⚠️ 注记是规范的灵魂：**踩过的坑、未实测的假设、口径差异必须写**——这是后来者不再犯错的唯一载体（先例：remove_song_from_playlist 的"点后行为未实测，按两态处理"三重评估）

## 3. 定位规范

- **坐标来源唯一性铁律（用户拍板 2026-10-12）**：运行时操作的坐标**只能**来自图像模板匹配或 OCR。经 UI 树/语义树（dump_nodes / accessibility）获取的任何坐标进入运行时点击/长按/滑动 = **违规**，无论场景、无论多方便。key 仅限 explorer 探索与调试（CLAUDE.md 规则 2）。

- 模板常量一律来自 `image/image_name_mapping.py`；**两态/多态元素成对登记**（如 `SWAN_PD_FAV_ON/OFF`），同形互扰风险高的加多模板链（glyph/浅底/深底三变体先例）
- **region 常量类级定义**：`_XXX_REGION = (x, y, w, h)`，注释必须写实测依据与**排除理由**（先例：`_PLAYLIST_SONGS_REGION` "下界 y=1370 在贴底播放条之上——不剔除会把歌曲名错配到播放条文本"）
- OCR 匹配统一走 compact 归一化（`_ocr_compact`/`_match_ocr_name`：去空格+l/I/1 易混映射），禁裸子串比较（OCR 吞空格属构造性 flaky，run6_clean2 实测）
- 动态内容（UUID/歌名/时间）不截图，走 OCR + region 限定
- 几何兜底仅限静态布局常量**：类级 `_XXX_TAP_X` 必须注释实测 bounds + "y 锚定 OCR 行，非盲坐标" + 兜底职能声明（模板命中时优先模板）

### 3.1 baseAW 能力不足时的处理（用户拍板 2026-10-12）

业务方法只允许调用 base 层（AWBase / 平台 base）**已封装**的操作。base 已有方法无法满足时：

- **禁止** `tap(x,y)` 凑合、**禁止**绕过 AWBase 直调 driver、**禁止**在业务方法里现写手势原语
- **停下上报用户**，说明三件事：①需要什么操作方式（例：长按拖动、双指缩放、边缘滑出）②作用于什么元素/什么场景 ③预期手势参数（时长/距离/方向）
- 由用户拍板后在 AWBase / 平台 base 补原语（CLAUDE.md 规则 1 流程），业务方法再调用——新方法顺带回填 AW 方法指南 §4

## 4. 操作四步验证链（每个元素操作必须走完，用户拍板 2026-10-12）

**① 页面证明 → ② 元素定位 → ③ 操作 → ④ 生效验证**，缺一步即违规：

1. **页面证明**：操作前先用"能证明所在页面"的锚点 [图]（页面特有控件图/根节点图）断言当前确实在目标页面。禁止"假设在目标页"直接找元素——页不对时元素搜索要么误匹配要么超时，归因困难。先例：`_preset_playing` 进我喜欢页前 `image_exists(SWAN_FAVORITE_PLAY_ALL)` 断言已到达。
2. **元素定位**：页面内寻找目标元素，**截图优先、OCR 兜底**（动态内容/多态背景才用 OCR），取得坐标。
3. **操作**：`click_image` / `click_text` / `drag_on_template` 等执行。
4. **生效验证**：操作后必须验证反应，按场景选最强证据：
   - **toast 提示**：`wait_toast`（动作后**立即**调用——toast 2~3.5s 即逝，期间不得插入其他截图/OCR）；
   - **页面切换**：断言下一页面锚点 [图]（先例：`_wait_player_page_open` 收起钮三模板）；
   - **状态变化**：目标态图标 [图] / OCR 文本出现（先例：`favorite_playlist` 收尾断言目标态图标；`select_device` 页头输出设备名 OCR 复核）。

   只点击不验证 = 违规（规则 6"只断言没异常"的操作版）。

## 5. 幂等与短路

- 导航/状态类方法**尽量幂等**：进方法先探测是否已在目标态（`_open_recent_played` 先 find 顶栏图；`favorite_playlist` 已在目标态不点；`select_device` 输出已=目标短路）
- 已知"重入会出问题"的场景（如 rig 行已选中态重入弹层导航分叉）**必须短路**并在 docstring 记录原因
- 方法的前置路由**复用既有方法**（如 favorite_playlist 复用 open_playlist_detail 的短路语义），不重写导航

## 6. 参数校验与错误

- 方法开头第一行校验枚举参数：`assert state in ("on","off","toggle"), "..."` 或 `raise ValueError(f"kind 仅支持 {sorted(...)}，收到 {kind!r}")`
- 错误消息带**当前值与合法值清单**，不做静默纠正

## 7. 日志、重试与失败即时截屏

- 日志按 CLAUDE.md 编码规范：`logger.info("✅ …")` / `logger.warning("⚠️ …")` / `logger.error("❌ …")`，中文
- 重试必须有界且透明：单次重试 + 证据帧引用（先例 start_play：失败取 `_latest_fail_shot()` 路径写进重试日志与最终断言消息）；**禁无限循环、禁静默重试**
- 探测类"可选命中"调用走 `_probe_image`（模板未入库防 assert 崩溃）

### 7.1 失败即时截屏落日志（用户拍板 2026-10-12）

AW 方法任一步骤报错（找不到目标图片 / OCR 超时 / 断言失败），必须**当即**截屏并保存进**该条用例**的执行日志：

- base 断言方法（`image_exists` / `click_image` / `wait_accessibility` 等）已由 `_screenshot_on_failure` 装饰器自动覆盖：失败即截 `output/screenshots/FAIL_<方法>_<时间戳>.png`（含 region 裁切图），自动内嵌该用例 HTML 日志（`output/logs/<用例名>.html`）与 Allure 附件——**优先复用这些方法做断言，失败证据零成本**
- 装饰器未覆盖的失败路径（查询型 `find_*` 返回 None 后的手工 assert 等）：assert 前先 `take_screenshot` 存证，路径写进断言消息（先例 `_latest_fail_shot`）
- 验收口径：**任何一条用例失败，其 HTML 日志里必须能看到失败现场截图**，否则视为违规

### 7.2 报告挂接策略（2026-10-12）

- SwanBusiness **公开方法一律挂 `@_aw_method_report`**（HTML 执行报告，`AW_REPORT` 默认开，`AW_REPORT=0` 关闭）
- mixin 方法（swan_regression.py）**不挂**装饰器：其内部调用的业务方法各自产出报告；业务方法互调走嵌套降级语义（内层不新建报告，步骤归档进外层同一份）——**一次顶层业务方法调用 = 一份完整报告**
- 报告证据帧复用定位截图流（AWBase 挂钩 cache_hit），**禁为报告新增独立截屏步骤**（性能约束：报告零额外截屏开销）

## 8. codegen 自检清单（提交前逐条过）

```
□ 类型注解完整，动作→None / 查询→值
□ docstring 六要素齐（身份/前置/定位/流程/断言/坑）
□ 枚举参数开头校验
□ 模板常量已登记；两态成对；region 有实测注记
□ OCR 比较走 compact 归一化
□ 坐标全部来自图/OCR——无 UI 树/key 坐标进运行时操作
□ 操作走四步验证链：页面证明→定位→操作→生效验证（④未漏）
□ baseAW 无对应原语时已停下上报，未自行凑合
□ 失败路径均即时截屏（装饰器覆盖或手工存证）
□ 幂等短路已考虑；前置复用既有方法
□ 无 tap 坐标 / 无 sleep 凑数 / 无 try-except 吞失败 / 无运行时 key
□ 重试有界且带证据帧
□ 已查 AW 方法指南确认无重复实现；新方法已回填指南 §2
```

## 9. 完整样板（真实代码摘录）

```python
def favorite_playlist(self, platform: str, state: str = "on",
                      timeout: float = 10.0) -> None:
    """歌单收藏/取消收藏（A29，回归用例41-43）。

    前置路由复用 open_playlist_detail（已在歌单详情页时短路）。收藏
    图标两态 [图]（域7 新截草稿）：state="on"/"off" 把图标置到目标态
    （已在目标态则不点）；"toggle" 翻转当前态。收尾断言目标态图标 [图]。
    ⚠️ 收藏结果持久化在账号收藏数据：用例层回滚用连续两次
    state="toggle"（无论初始态如何，两次翻转后回到原态）。
    """
    assert state in ("on", "off", "toggle"), "state 仅支持 on / off / toggle"
    self.open_playlist_detail(platform)
    current = self._playlist_fav_state()
    assert current is not None, (
        "歌单详情页未识别收藏图标态（两态模板均未匹配，请核对截图质量或页面改版）")
    target = state if state in ("on", "off") else ("off" if current == "on" else "on")
    if current != target:
        self.click_image(SWAN_PD_FAV_ON if current == "on" else SWAN_PD_FAV_OFF,
                         timeout=5)
    self.image_exists(SWAN_PD_FAV_ON if target == "on" else SWAN_PD_FAV_OFF,
                      timeout=timeout)

def _playlist_fav_state(self) -> str | None:
    """歌单详情页收藏图标当前态：on / off / None（两态模板都未匹配）。"""
    if self.find_image(SWAN_PD_FAV_ON, timeout=2) is not None:
        return "on"
    if self.find_image(SWAN_PD_FAV_OFF, timeout=2) is not None:
        return "off"
    return None
```
