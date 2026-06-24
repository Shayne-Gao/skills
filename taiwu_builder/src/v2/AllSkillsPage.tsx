import { useMemo, useState } from "react";
import { allFactions, allCategories, skills } from "@/utils/taiwuData";
import SkillChip from "./SkillChip";
import { useSkillHover } from "./useSkillHover";
import { GRADE_COLORS } from "./gameColors";

// 截图中行标题的展示顺序与合并方式
const ROW_DEFS: Array<{ label: string; categories: string[] }> = [
  { label: "内功", categories: ["内功"] },
  { label: "身法", categories: ["身法"] },
  { label: "绝技", categories: ["绝技"] },
  { label: "剑法", categories: ["剑法"] },
  { label: "刀法", categories: ["刀法"] },
  { label: "长兵", categories: ["长兵"] },
  { label: "御射", categories: ["御射"] },
  { label: "拳掌", categories: ["拳掌"] },
  { label: "指法", categories: ["指法"] },
  { label: "腿法", categories: ["腿法"] },
  { label: "暗器", categories: ["暗器"] },
  { label: "奇门", categories: ["奇门"] },
  { label: "软兵", categories: ["软兵"] },
  { label: "乐器", categories: ["乐器"] },
];

// 品阶排序：凡 < 下 < 中 < 上 < 奇 < 秘 < 极 < 超 < 绝 < 神（从低到高）
const GRADE_ORDER: Record<string, number> = {
  "凡·十品": 0,
  "下·九品": 1,
  "中·八品": 2,
  "上·七品": 3,
  "奇·六品": 4,
  "秘·五品": 5,
  "极·四品": 6,
  "超·三品": 7,
  "绝·二品": 8,
  "神·一品": 9,
};

const FACTION_TABS = ["全部", ...allFactions];

/**
 * 全部功法一览：门派 tab + 行分类 + chips
 */
export default function AllSkillsPage() {
  const [faction, setFaction] = useState<string>("全部");
  const { onEnter, onLeave, hoverNode } = useSkillHover();

  // 过滤 + 按 category 分组
  const grouped = useMemo(() => {
    const filtered = skills.filter((s) => (faction === "全部" ? true : s.faction === faction));
    const map = new Map<string, typeof skills>();
    for (const s of filtered) {
      const cat = s.category || "其它";
      if (!map.has(cat)) map.set(cat, [] as typeof skills);
      map.get(cat)!.push(s);
    }
    // 行内排序：品阶从低到高，同品阶按 id 升序
    for (const arr of map.values()) {
      arr.sort((a, b) => {
        const ga = GRADE_ORDER[a.grade ?? ""] ?? 99;
        const gb = GRADE_ORDER[b.grade ?? ""] ?? 99;
        if (ga !== gb) return ga - gb;
        return Number(a.id) - Number(b.id);
      });
    }
    return map;
  }, [faction]);

  // 按 ROW_DEFS 顺序展示，再追加未覆盖的剩余分类
  const visibleRows = useMemo(() => {
    const used = new Set<string>();
    const out: Array<{ label: string; items: typeof skills }> = [];
    for (const def of ROW_DEFS) {
      const items: typeof skills = [];
      for (const cat of def.categories) {
        const got = grouped.get(cat);
        if (got) items.push(...got);
        used.add(cat);
      }
      if (items.length) out.push({ label: def.label, items });
    }
    for (const [cat, arr] of grouped.entries()) {
      if (!used.has(cat) && arr.length) out.push({ label: cat, items: arr });
    }
    return out;
  }, [grouped]);

  return (
    <div className="min-h-[calc(100vh-100px)] bg-[#0b0b0c] text-[#f4ecd8]">
      <main className="px-5 pb-10 pt-4">
        <div className="flex items-baseline justify-between">
          <h1 className="font-serif text-3xl tracking-wider text-[#f4ecd8]">功法一览</h1>
          <p className="text-[13px] text-[#9a927d]">
            数据源：太吾绘卷 wiki · 共 {allCategories.length} 类 / {skills.length} 条
          </p>
        </div>

        {/* 门派 tab */}
        <div className="mt-4 flex flex-wrap items-center gap-1.5">
          <span className="mr-1 rounded-sm bg-[#caa75a] px-2 py-1 text-[13px] text-[#1a1812]">门派</span>
          {FACTION_TABS.map((f) => {
            const active = f === faction;
            return (
              <button
                key={f}
                onClick={() => setFaction(f)}
                className={`rounded-sm border px-2.5 py-1 text-[13px] transition ${
                  active
                    ? "border-[#caa75a]/70 bg-[#caa75a]/15 text-[#f4ecd8]"
                    : "border-[#caa75a]/15 bg-[#15140f] text-[#c9c2af] hover:border-[#caa75a]/40 hover:text-[#f4ecd8]"
                }`}
              >
                {f}
              </button>
            );
          })}
        </div>

        {/* 行分类展示 */}
        <div className="mt-4 overflow-hidden rounded-2xl border border-[#caa75a]/25 bg-[#15140f] shadow-[0_8px_28px_rgba(0,0,0,0.6)]">
          {visibleRows.length === 0 ? (
            <div className="px-5 py-8 text-center text-[14px] text-[#9a927d]">
              当前筛选下没有功法
            </div>
          ) : (
            visibleRows.map(({ label, items }, idx) => (
              <div
                key={label}
                className={`flex items-stretch gap-3 px-3 py-2.5 ${
                  idx === visibleRows.length - 1 ? "" : "border-b border-[#caa75a]/15"
                }`}
              >
                <div className="flex w-[78px] shrink-0 items-center justify-center rounded-md bg-[#1c1a14] px-1 py-1 text-center font-serif text-[14px] tracking-wider text-[#f4ecd8] border border-[#caa75a]/20">
                  {label}
                </div>
                <div className="flex min-w-0 flex-1 flex-wrap items-center gap-1.5">
                  {items.map((s) => (
                    <SkillChip key={s.id} skill={s} onEnter={onEnter} onLeave={onLeave} />
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* 品阶色例 */}
        <div className="mt-3 flex flex-wrap items-center gap-2 text-[12px] text-[#9a927d]">
          <span>品阶配色：</span>
          {Object.entries(GRADE_COLORS).map(([g, c]) => (
            <span key={g} className="rounded-sm border border-[#caa75a]/15 px-1.5 py-0.5">
              <span style={{ color: c }}>{g}</span>
            </span>
          ))}
        </div>
      </main>
      {hoverNode}
    </div>
  );
}
