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

- 模板常量一律来自 `image/image_name_mapping.py`；**两态/多态元素成对登记**（如 `SWAN_PD_FAV_ON/OFF`），同形互扰风险高的加多模板链（glyph/浅底/深底三变体先例）
- **region 常量类级定义**：`_XXX_REGION = (x, y, w, h)`，注释必须写实测依据与**排除理由**（先例：`_PLAYLIST_SONGS_REGION` "下界 y=1370 在贴底播放条之上——不剔除会把歌曲名错配到播放条文本"）
- OCR 匹配统一走 compact 归一化（`_ocr_compact`/`_match_ocr_name`：去空格+l/I/1 易混映射），禁裸子串比较（OCR 吞空格属构造性 flaky，run6_clean2 实测）
- 动态内容（UUID/歌名/时间）不截图，走 OCR + region 限定
- **几何兜底仅限静态布局常量**：类级 `_XXX_TAP_X` 必须注释实测 bounds + "y 锚定 OCR 行，非盲坐标" + 兜底职能声明（模板命中时优先模板）

## 4. 断言收尾（CLAUDE.md 规则 6 细化）

- 每个动作方法**最后一个操作必须是可观察状态断言**：`image_exists` / `text_exists` / 双证据组合（assert_playing：⏸ [图] + 黑胶动检或进度递增）
- 断言失败消息三要素：**没找到什么 + 已核对什么 + 排查方向**（先例："歌单详情页未识别收藏图标态（两态模板均未匹配，请核对截图质量或页面改版）"）
- 禁止"只断言没异常"、禁止 try/except 吞失败、禁止坐标回退（规则 6/7/10）

## 5. 幂等与短路

- 导航/状态类方法**尽量幂等**：进方法先探测是否已在目标态（`_open_recent_played` 先 find 顶栏图；`favorite_playlist` 已在目标态不点；`select_device` 输出已=目标短路）
- 已知"重入会出问题"的场景（如 rig 行已选中态重入弹层导航分叉）**必须短路**并在 docstring 记录原因
- 方法的前置路由**复用既有方法**（如 favorite_playlist 复用 open_playlist_detail 的短路语义），不重写导航

## 6. 参数校验与错误

- 方法开头第一行校验枚举参数：`assert state in ("on","off","toggle"), "..."` 或 `raise ValueError(f"kind 仅支持 {sorted(...)}，收到 {kind!r}")`
- 错误消息带**当前值与合法值清单**，不做静默纠正

## 7. 日志与重试

- 日志按 CLAUDE.md 编码规范：`logger.info("✅ …")` / `logger.warning("⚠️ …")` / `logger.error("❌ …")`，中文
- 重试必须有界且透明：单次重试 + 证据帧引用（先例 start_play：失败取 `_latest_fail_shot()` 路径写进重试日志与最终断言消息）；**禁无限循环、禁静默重试**
- 探测类"可选命中"调用走 `_probe_image`（模板未入库防 assert 崩溃）

## 8. codegen 自检清单（提交前逐条过）

```
□ 类型注解完整，动作→None / 查询→值
□ docstring 六要素齐（身份/前置/定位/流程/断言/坑）
□ 枚举参数开头校验
□ 模板常量已登记；两态成对；region 有实测注记
□ OCR 比较走 compact 归一化
□ 收尾是可观察状态断言，失败消息三要素
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
