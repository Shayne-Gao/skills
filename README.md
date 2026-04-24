# Skills Collection

这个仓库用于存放多个 Trae / Lark CLI 风格的 skills。每个 skill 都是一个相对独立的目录（包含其 `SKILL.md`、模板/脚本/资源等），可以单独演进与使用。

## 目录结构

- `/<skill-name>/`
  - `SKILL.md`：该 skill 的工作流说明与使用规范（强约束与验收标准也会沉淀在这里）
  - `template*.html`：输出 HTML 的模板（如国内/国际不同版本）
  - `scripts/`：可选的辅助脚本（生成/修复/测试等）

当前仓库包含：
- `travel-planner/`：旅行计划生成器（输出 Markdown + 单文件 HTML 地图行程）

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

- 每新增一个 skill：创建同名目录，并提供 `SKILL.md` 作为入口文档
- 重要经验与“避免踩坑”的规则：优先沉淀到对应 skill 的 `SKILL.md`
