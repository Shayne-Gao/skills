# Skills Collection

这个仓库用于存放多个 Trae / Lark CLI 风格的 skills。每个 skill 都是一个相对独立的目录，包含自己的 `SKILL.md`、模板、脚本、文档与资源，可以单独演进与使用。

## 仓库约定

- 所有 skill 在仓库根目录平铺展示，根目录下的各个 skill 文件夹是唯一事实来源。
- `.trae/skills/` 仅保留兼容入口，内部通过软链接指向根目录对应 skill，避免出现两份内容长期分叉。
- 后续维护时，优先直接修改根目录的 skill 文件夹；如果从 `.trae/skills/` 路径进入，由于它指向同一份目录，修改也会落到正确位置。

## 目录结构

- `/<skill-name>/`
  - `SKILL.md`：该 skill 的工作流说明与使用规范
  - `docs/` / `references/`：可选的补充文档与知识库
  - `template*.html`：可选的 HTML 模板
  - `scripts/`：可选的辅助脚本（生成、修复、测试等）

当前仓库包含这些根目录 skill：
- `agent-reach/`：互联网调研与多平台内容抓取路由
- `fetch_smzdm_latest_items/`：什么值得买最新商品抓取与历史比价
- `sg-local-activity-deals/`：新加坡本地活动与优惠信息调研
- `shopping-category-buyer-guide/`：品类选购指南与推荐整合
- `travel-planner/`：旅行计划生成器，输出 Markdown + 单文件 HTML 地图行程
- `wuwa-account-cultivation-planner/`：鸣潮账号养成规划
- `wuwa-account-evaluator/`：鸣潮账号市场刷新、评分与候选比较

## 兼容入口

为了兼容本地 Trae 的既有读取路径，仓库保留：

- `.trae/skills/<skill-name> -> ../../<skill-name>`

如果你在别的机器重新 clone 后发现软链接异常，可以在仓库根目录执行：

```bash
bash scripts/relink_trae_skills.sh
```

## 与本机 Trae 统一

如果你希望本机全局 `~/.trae/skills/` 里的自定义 skill 也统一指向这个 GitHub 仓库，执行：

```bash
bash scripts/link_global_trae_skills.sh
```

这个脚本会：

- 以仓库根目录 skill 作为唯一事实来源
- 先备份 `~/.trae/skills/` 里已有的同名自定义 skill
- 再把这些全局 skill 改成指向仓库根目录的软链接

执行完成后，你无论是在这个仓库里改 skill，还是在别的对话里通过 `~/.trae/skills/` 路径改 skill，最终都会落到 GitHub 仓库中的同一份目录。

如需检查当前是否已经统一，可执行：

```bash
bash scripts/check_skill_layout.sh
```

## travel-planner

`travel-planner` 用于生成可分享的单文件 HTML 行程页，支持：
- 地图点位按天分色（D1/D2/D3…），并按天连线
- 国内默认使用高德底图（Leaflet），并进行坐标系处理
- 内外链分离：点击景点名只在页面内定位；点击 🗺️ 才允许外跳地图
- 稳定性规则与验收清单全部记录在 `travel-planner/SKILL.md`

### 快速开始（本地预览）

在仓库根目录启动静态服务（任选其一）：

```bash
python3 -m http.server 8890 --directory ./travel-planner
```

然后打开生成的 HTML（示例）：
- `http://localhost:8890/outputs/Trip_Plan_Shanghai_Test_3D.html`

### 测试用生成脚本

`travel-planner/scripts/` 下包含若干测试脚本，用于快速生成“仅用于验证 HTML”的行程：
- `generate_tianjin_jizhou_test.py`
- `generate_shanghai_test_3d.py`
- `generate_quanzhou_daytrip.py`

运行示例：

```bash
python3 travel-planner/scripts/generate_shanghai_test_3d.py
```

生成文件位于 `travel-planner/outputs/`：
- `Trip_Plan_*.html`
- `Trip_Plan_*.md`

## 贡献方式

- 每新增一个 skill：直接在仓库根目录创建同名目录，并提供 `SKILL.md` 作为入口文档
- 如果需要兼容 `.trae/skills/` 入口，同步更新软链接，或直接执行 `bash scripts/relink_trae_skills.sh`
- 重要经验与“避免踩坑”的规则：优先沉淀到对应 skill 的 `SKILL.md`
