// 太吾绘卷游戏内的官方色板，从 wiki raw_html 中提取得到。
// 用于让 v2 的功法卡、hover、Picker 与游戏视觉对齐。

// 品阶 → 名字颜色（功法名按品阶染色）
export const GRADE_COLORS: Record<string, string> = {
  "神·一品": "#E4504D",
  "绝·二品": "#C77BE6",
  "超·三品": "#B97BD1",
  "极·四品": "#F4B73B",
  "秘·五品": "#F4D03F",
  "奇·六品": "#5DA8E8",
  "上·七品": "#8FBAE7",
  "中·八品": "#FBFBFB",
  "下·九品": "#FBFBFB",
  "凡·十品": "#9CA3AF",
};

// 路线（混元/归元/纯阳/玄阴/金刚）颜色
export const ROUTE_COLORS: Record<string, string> = {
  归元: "#6DB75F",
  混元: "#F4D03F",
  纯阳: "#E4504D",
  玄阴: "#8FBAE7",
  金刚: "#F4B73B",
};

// 心法正/逆练标题颜色
export const PRACTICE_COLORS: Record<"正练" | "逆练", string> = {
  正练: "#8FBAE7",
  逆练: "#E4504D",
};

// 不传之秘 / 强调
export const ACCENT_RED = "#E4504D";

// 形状 ◇
export const SHAPE_COLOR = "#FBFBFB";

// hover 卡的整体主题
export const HOVER_THEME = {
  bg: "#0b0b0c",
  border: "#caa75a",
  text: "#f4ecd8",
  subText: "#c9c2af",
  divider: "#3a3424",
};

export function getGradeColor(grade: string | null | undefined) {
  if (!grade) return "#FBFBFB";
  return GRADE_COLORS[grade] ?? "#FBFBFB";
}

export function getRouteColor(route: string | null | undefined) {
  if (!route) return "#FBFBFB";
  return ROUTE_COLORS[route] ?? "#FBFBFB";
}
