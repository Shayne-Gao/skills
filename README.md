# Skills Collection

这个仓库是我的自定义 skill 与相关项目工作区，主要用于沉淀可复用的 Agent skill、配套脚本、研究资料和部分独立项目型目录。

## 仓库规则

- 根目录下的各个 skill 文件夹是实际内容与唯一事实来源。
- 仓库内 `.trae/skills/` 只作为兼容入口，通过软链接指向根目录对应 skill。
- 后续维护时优先直接修改根目录 skill；如果从 `.trae/skills/` 路径进入，改动也会落到同一份内容。

## 根目录 Skill 总览

下面这些目录是当前仓库里真正按 skill 方式维护的主要能力：

- `agent-reach/`：互联网调研路由 skill，用于全网搜索、平台内容抓取、网页文章获取与多平台信息调研。
- `fetch_smzdm_latest_items/`：抓取什么值得买最新商品、保存完整快照、比对历史记录并输出推荐结果。
- `sg-local-activity-deals/`：面向新加坡本地活动与优惠的信息搜集，兼顾平台内容与官方信息核验。
- `shopping-category-buyer-guide/`：围绕某个商品品类做选购指南，整合近期好价、规格参数、评价和推荐逻辑。
- `travel-planner/`：生成旅行规划与可分享 HTML 行程页，支持地图标点、按天连线和单文件展示。
- `wuwa-account-cultivation-planner/`：根据已有鸣潮账号角色与资源情况，输出养成优先级与配队规划。
- `wuwa-account-evaluator/`：刷新鸣潮账号市场数据、统一评分并做候选账号比较。

## 其他根目录内容

除了 skill，本仓库还包含一些支撑目录或独立项目目录：

- `agent-onboarding/`：给产品经理使用 Agent 的实战教程与课程文档。
- `agent-onboarding-site/`：`agent-onboarding` 的站点化或展示化产物目录。
- `game-account-evaluator/`：通用游戏账号评估脚本与数据工作区，是 `wuwa-account-evaluator/` 的底层业务项目之一。
- `repo_tools/`：仓库级维护脚本，负责软链接重建、全局 Trae 统一和结构检查。
- `shopping-research/`：购物研究资料、对比表、价格历史与选购输出。
- `taiwu_builder/`：太吾绘卷相关构筑器或配装研究项目目录。
- `workspace_projects/`：各类底层工作项目与抓取工程目录。
- `哈利波特魔术策划案设计师/`：哈利波特主题亲子魔术策划案项目资料目录，沉淀剧本、执行稿、飞书文档草稿与验证记录。

`html_demo` 已独立维护在单独仓库：[Shayne-Gao/html_demo](https://github.com/Shayne-Gao/html_demo)，不再作为本仓库的组成部分。

## 兼容与同步

为了兼容本地 Trae 既有读取路径，仓库保留：

- `.trae/skills/<skill-name> -> ../../<skill-name>`

如果你在别的机器重新 clone 后发现仓库内软链接异常，可以执行：

```bash
bash repo_tools/relink_trae_skills.sh
```

如果你希望本机全局 `~/.trae/skills/` 里的自定义 skill 也统一指向这个 GitHub 仓库，可以执行：

```bash
bash repo_tools/link_global_trae_skills.sh
```

这个脚本会先备份已有同名 skill，再把全局 Trae 入口改成指向仓库根目录的软链接。

如需检查当前是否已经统一，可执行：

```bash
bash repo_tools/check_skill_layout.sh
```

## 常用示例

`travel-planner` 是当前最完整的 HTML 输出型 skill，常用本地预览方式：

```bash
python3 -m http.server 8890 --directory ./travel-planner
```

示例生成脚本：

```bash
python3 travel-planner/scripts/generate_shanghai_test_3d.py
```

## 维护约定

- 每新增一个 skill：直接在仓库根目录创建同名目录，并提供 `SKILL.md` 作为入口文档。
- 如果需要兼容 `.trae/skills/` 入口，同步更新软链接，或直接执行 `bash repo_tools/relink_trae_skills.sh`。
- 重要经验、约束和避免踩坑的规则，优先沉淀到对应 skill 的 `SKILL.md`。
