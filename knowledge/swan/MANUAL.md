# Swan 知识库说明书(knowledge/swan)

> 版本:2026-09-11 · 维护:测试部 · 权威数字来源:2026-09-11 三机实仓审计(.229 汇总,见 `claude-shared/tasks/kb-verify/229-summary.md`)

## 1. 这是什么

Swan 知识库是 Swan App(Android / Flutter,`com.swan.network`)的**已验证 UI 知识集合**:48 个页面文档、62 组元素截图与常量、跨页面功能/流程索引。它同时服务三种读者:

- **人**:了解每个页面怎么进、有什么元素、怎么断言
- **pytest 自动化**:页面文档 + app_map 可直接生成测试用例(SwanBusiness 层)
- **MCP / 向量检索**:`knowledge_graph_swan` / `vector_kb_swan` 双层索引供 agent 查询

核心纪律:**只写真事实**——页面事实必须经真机探索或测试实际验证后写入,禁止猜测;与其他项目知识完全隔离。

## 2. 位置与隔离

| 项 | 值 |
|---|---|
| 仓库 | uiautotest(工作副本:各开发机+平台机 .167 `/opt/uiautotest`,远端 GitLab) |
| KB 根目录 | `E:\uiautotest\knowledge\swan\` |
| 兄弟知识库 | `knowledge/web`(TidiTree Web)、`knowledge/android`(音箱屏 Android)——**严禁跨库引用路由/定位器/页面结构** |
| 测试对象 | 真机 c0614b6a(OPPO,Android 11,720x1600),app v5.3.0 |
| 定位策略 | 无障碍键 > OCR 文本 > 图像模板,**禁止坐标** |

## 3. 架构层级

```text
uiautotest/
├── knowledge/
│   ├── swan/                     ← 本知识库
│   │   ├── README.md             # 入口:隔离原则、五要素门槛(状态节已过期,见 §7)
│   │   ├── CONTRIBUTING.md       # 写法标准:frontmatter、动态/静态判定、断言/截图规范
│   │   ├── app_map.json          # 机读主索引:48 页面条目 + 转场 + 功能分类
│   │   ├── backlinks.json        # [[wikilink]] 反向索引(graph 层)
│   │   ├── pages/                # 48 个已验证页面文档(正式知识)
│   │   ├── draft/                # 探索草稿(验证通过转正;当前已空)
│   │   ├── digest/
│   │   │   ├── 中文索引.md / 页面覆盖对照.md
│   │   │   ├── features/         # 7 个功能域全景(账号体系/导航框架/收藏管理/设备管理/平台聚合/播放器/帮助与关于)
│   │   │   └── flows/            # 6 条端到端流程(登录/搜索/收藏/歌单/导航等)
│   │   ├── templates/            # page.md / feature.md / flow.md 三个写作模板
│   │   └── .chroma_db/           # 向量索引(Chroma,embedding 增量更新)
│   ├── android/                  ← 兄弟库,互不引用
│   └── web/                      ← 兄弟库,互不引用
├── image/
│   ├── flutter/                  # 62 张已转正元素截图(swan_页面_元素.png)
│   ├── image_ai/flutter/         # 新图暂存区(draft=True 注册)
│   └── image_name_mapping.py     # 62 个 SWAN_* 常量 ↔ png 一一对应
└── scripts/knowledge/            # backlinks_generator.py / embedding_pipeline.py
```

## 4. 数据流(知识生命周期)

```text
真机探索 ──→ draft/*.md(草稿)
              │  五要素齐 + 真机验证通过
              ▼
         pages/*.md(转正,frontmatter 完整)──→ 更新 app_map.json
新元素截图 ──→ image_ai/flutter/(draft=True 注册)
              │  aw-verify 用例跑通
              ▼
         image/flutter/ + image_name_mapping.py(promote_image())

git commit ──→ post-commit hook → auto_update.py
                 ├─ backlinks_generator.py      (graph 层)
                 └─ embedding_pipeline.py --incremental (vector 层)
```

## 5. 各层职责速览

| 层 | 内容 | 谁读 |
|---|---|---|
| pages/(48 页) | 每页:概述/生效断言/进入方式/关键元素/布局/关联,frontmatter 必填 | 人 + 用例生成 + MCP |
| app_map.json | meta(包名/驱动/设备/定位策略)+ pages 索引 + transitions(31 页转场)+ feature_categories(7) | pytest 生成 + agent |
| digest/features(7 篇) | 按功能域组织的跨页面全景 | 人(设计用例时) |
| digest/flows(6 篇) | 可自动化端到端路径,步骤表直译 SwanBusiness 方法调用 | pytest 生成 |
| image 层 | 62 常量 ↔ 62 图,截图规范 `swan_{页面}_{元素}.png` 三段式 | image_exists / click_image |
| 双索引层 | backlinks.json(wikilink 图)+ .chroma_db(向量) | knowledge_graph_swan / vector_kb_swan MCP |

## 6. 权威数字(2026-09-11 实仓复核)

| 项 | 数值 |
|---|---|
| 页面文档 | 48(34 带 frontmatter / 14 旧格式待迁移) |
| app_map 页面条目 | 48(verified 33 / page 15) |
| SWAN_* 常量 ↔ image/flutter png | 62 : 62 一一对应,零缺失零悬空 |
| feature / flow 文档 | 7 / 6 |
| 图片目录 | 仓库根 `image/flutter/`(⚠ 不在 knowledge/swan 下) |

## 7. 已知问题与待办(详见 229-summary.md)

1. `app_map.json` 12 条 doc 链接指向已空的 `draft/`(草稿转正后未同步)—— 待改 pages/
2. 14 页旧格式(无 frontmatter)—— 按 `templates/page.md` 迁移
3. 42 张元素图暂无页面文档引用(对应"verified 但文档未写"页面)—— 补文档时挂接
4. 本库 README.md"当前状态"节(15 页,2026-09-08)已过期,以本说明书 §6 为准

## 8. 怎么用

- **查一页**:`pages/swan_<页面名>.md`;查上下游走 frontmatter 关联 + backlinks
- **查元素**:先 `image_name_mapping.py` 找常量,再按 CONTRIBUTING §2 判定静态/动态选择定位策略
- **跑索引重建**:`python scripts/knowledge/backlinks_generator.py --knowledge-dir knowledge/swan` + `python scripts/knowledge/embedding_pipeline.py --knowledge-dir knowledge/swan --chroma-dir knowledge/swan/.chroma_db --incremental`
- **贡献新页**:读 CONTRIBUTING.md,严格走 draft → 转正流程
