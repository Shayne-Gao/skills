import { useEffect, useMemo, useState } from "react";
import { curatedRecommendations, getSkillById } from "@/utils/taiwuData";
import SkillChip from "./SkillChip";
import { useSkillHover } from "./useSkillHover";
import { useV2Store } from "./store";

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

function collectPracticeModes(prefix?: string | null) {
  if (prefix === "正·") return new Set(["正"]);
  if (prefix === "逆·") return new Set(["逆"]);
  if (prefix === "正/逆·") return new Set(["正", "逆"]);
  return new Set<string>();
}

function mergeDisplayPrefix(prefixes: Array<string | null | undefined>) {
  const modes = new Set<string>();
  let hasGeneric = false;
  for (const prefix of prefixes) {
    if (!prefix) {
      hasGeneric = true;
      continue;
    }
    if (prefix === "正/逆·") {
      hasGeneric = true;
      modes.add("正");
      modes.add("逆");
      continue;
    }
    collectPracticeModes(prefix).forEach((mode) => modes.add(mode));
  }
  if (modes.has("正") && modes.has("逆")) return "正/逆·";
  if (modes.has("正")) return "正·";
  if (modes.has("逆")) return "逆·";
  if (hasGeneric) return "正/逆·";
  return "正/逆·";
}

type ShoppingItem = {
  skillId: string;
  prefix: string;
  faction: string;
  category: string;
  grade: string;
  recommended: boolean;
  recommendationSources: Array<{
    label: string;
    reasons: string[];
  }>;
  buildIds: string[];
  buildNames: string[];
};

export default function FactionShoppingPage() {
  const { onEnter, onLeave, hoverNode } = useSkillHover();
  const builds = useV2Store((s) => s.builds);
  const [activeFaction, setActiveFaction] = useState("全部");
  const [activeCategory, setActiveCategory] = useState("全部");
  const [activeGrade, setActiveGrade] = useState("全部");
  const [activeBuildId, setActiveBuildId] = useState("全部");
  const [hoveredReasonSourceKey, setHoveredReasonSourceKey] = useState<string | null>(null);

  const recommendationMap = useMemo(() => {
    const grouped = new Map<
      string,
      {
        prefixes: string[];
        sourceReasons: Map<string, Set<string>>;
      }
    >();
    curatedRecommendations.forEach((tab) => {
      tab.rows.forEach((row) => {
        row.skill_ids.forEach((id, index) => {
          const prefix = row.skill_prefixes?.[index] ?? null;
          if (!grouped.has(id)) grouped.set(id, { prefixes: [], sourceReasons: new Map() });
          grouped.get(id)!.prefixes.push(prefix ?? "正/逆·");
          if (row.recommendation_reason?.trim()) {
            const source = row.source_label?.trim() || "综合整理";
            if (!grouped.get(id)!.sourceReasons.has(source)) {
              grouped.get(id)!.sourceReasons.set(source, new Set<string>());
            }
            grouped.get(id)!.sourceReasons.get(source)!.add(row.recommendation_reason.trim());
          }
        });
      });
    });
    return grouped;
  }, []);

  const buildRequirementMap = useMemo(() => {
    const grouped = new Map<
      string,
      {
        prefixes: string[];
        buildIds: Set<string>;
        buildNames: Set<string>;
      }
    >();
    builds.forEach((build) => {
      Object.values(build.sections).forEach((slots) => {
        slots.forEach((slot) => {
          if (!slot.skillId) return;
          if (!grouped.has(slot.skillId)) {
            grouped.set(slot.skillId, {
              prefixes: [],
              buildIds: new Set<string>(),
              buildNames: new Set<string>(),
            });
          }
          const item = grouped.get(slot.skillId)!;
          item.prefixes.push(slot.practiceMode === "正练" ? "正·" : "逆·");
          item.buildIds.add(build.id);
          item.buildNames.add(build.name);
        });
      });
    });
    return grouped;
  }, [builds]);

  const shoppingItems = useMemo(() => {
    const skillIds = new Set<string>([
      ...Array.from(recommendationMap.keys()),
      ...Array.from(buildRequirementMap.keys()),
    ]);
    const items: ShoppingItem[] = [];
    skillIds.forEach((skillId) => {
      const skill = getSkillById(skillId);
      if (!skill?.faction || !skill.category || !skill.grade) return;
      const rec = recommendationMap.get(skillId);
      const build = buildRequirementMap.get(skillId);
      items.push({
        skillId,
        prefix: mergeDisplayPrefix([...(rec?.prefixes ?? []), ...(build?.prefixes ?? [])]),
        faction: skill.faction,
        category: skill.category,
        grade: skill.grade,
        recommended: !!rec,
        recommendationSources: Array.from(rec?.sourceReasons.entries() ?? []).map(([label, reasons]) => ({
          label,
          reasons: Array.from(reasons),
        })),
        buildIds: Array.from(build?.buildIds ?? []),
        buildNames: Array.from(build?.buildNames ?? []),
      });
    });
    return items.sort((a, b) => {
      const ga = GRADE_ORDER[a.grade] ?? 99;
      const gb = GRADE_ORDER[b.grade] ?? 99;
      if (ga !== gb) return ga - gb;
      return Number(a.skillId) - Number(b.skillId);
    });
  }, [buildRequirementMap, recommendationMap]);

  const factionTabs = useMemo(
    () => ["全部", ...Array.from(new Set(shoppingItems.map((item) => item.faction))).sort()],
    [shoppingItems],
  );
  const categoryTabs = useMemo(() => {
    const categories = new Set(shoppingItems.map((item) => item.category));
    const ordered = ROW_DEFS.flatMap((def) => def.categories).filter((category) => categories.has(category));
    const extra = Array.from(categories).filter((category) => !ordered.includes(category)).sort();
    return ["全部", ...ordered, ...extra];
  }, [shoppingItems]);
  const gradeTabs = useMemo(() => {
    const grades = new Set(shoppingItems.map((item) => item.grade));
    return [
      "全部",
      ...Object.keys(GRADE_ORDER)
        .filter((grade) => grade !== "凡·十品" && grades.has(grade))
        .sort((a, b) => (GRADE_ORDER[a] ?? 99) - (GRADE_ORDER[b] ?? 99)),
    ];
  }, [shoppingItems]);
  const buildTabs = useMemo(
    () => [{ id: "全部", label: "全部" }, ...builds.map((build) => ({ id: build.id, label: build.name }))],
    [builds],
  );

  useEffect(() => {
    if (!factionTabs.includes(activeFaction)) setActiveFaction("全部");
  }, [activeFaction, factionTabs]);
  useEffect(() => {
    if (!categoryTabs.includes(activeCategory)) setActiveCategory("全部");
  }, [activeCategory, categoryTabs]);
  useEffect(() => {
    if (!gradeTabs.includes(activeGrade)) setActiveGrade("全部");
  }, [activeGrade, gradeTabs]);
  useEffect(() => {
    if (!buildTabs.some((build) => build.id === activeBuildId)) setActiveBuildId("全部");
  }, [activeBuildId, buildTabs]);

  const filteredItems = useMemo(
    () =>
      shoppingItems.filter((item) => {
        if (activeBuildId !== "全部" && !item.buildIds.includes(activeBuildId)) return false;
        if (activeFaction !== "全部" && item.faction !== activeFaction) return false;
        if (activeCategory !== "全部" && item.category !== activeCategory) return false;
        if (activeGrade !== "全部" && item.grade !== activeGrade) return false;
        return true;
      }),
    [activeBuildId, activeCategory, activeFaction, activeGrade, shoppingItems],
  );

  const visibleRows = useMemo(() => {
    const grouped = new Map<string, ShoppingItem[]>();
    filteredItems.forEach((item) => {
      if (!grouped.has(item.category)) grouped.set(item.category, []);
      grouped.get(item.category)!.push(item);
    });
    const used = new Set<string>();
    const rows: Array<{ label: string; items: ShoppingItem[] }> = [];
    ROW_DEFS.forEach((def) => {
      const items = def.categories.flatMap((category) => grouped.get(category) ?? []);
      def.categories.forEach((category) => used.add(category));
      if (items.length) rows.push({ label: def.label, items });
    });
    grouped.forEach((items, category) => {
      if (!used.has(category)) rows.push({ label: category, items });
    });
    return rows;
  }, [filteredItems]);

  return (
    <div className="min-h-[calc(100vh-100px)] bg-[#0b0b0c] text-[#f4ecd8]">
      <main className="px-5 pb-10 pt-4">
        <div className="flex items-baseline justify-between">
          <h1 className="font-serif text-3xl tracking-wider text-[#f4ecd8]">门派购物清单</h1>
          <p className="text-[13px] text-[#9a927d]">
            汇总推荐功法 + 当前 Build 所需功法，可按 Build / 门派 / 分类 / 品阶筛选
          </p>
        </div>

        <div className="mt-3 rounded-2xl border border-[#caa75a]/25 bg-[#15140f] px-3 py-3 shadow-[0_8px_28px_rgba(0,0,0,0.6)]">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="mr-1 rounded-sm bg-[#caa75a] px-2 py-1 text-[13px] text-[#1a1812]">Build</span>
            {buildTabs.map((build) => {
              const active = build.id === activeBuildId;
              return (
                <button
                  key={build.id}
                  type="button"
                  onClick={() => setActiveBuildId(build.id)}
                  className={`rounded-sm border px-2.5 py-1 text-[13px] transition ${
                    active
                      ? "border-[#caa75a]/70 bg-[#caa75a]/15 text-[#f4ecd8]"
                      : "border-[#caa75a]/15 bg-[#15140f] text-[#c9c2af] hover:border-[#caa75a]/40 hover:text-[#f4ecd8]"
                  }`}
                >
                  {build.label}
                </button>
              );
            })}
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-1.5">
            <span className="mr-1 rounded-sm bg-[#caa75a] px-2 py-1 text-[13px] text-[#1a1812]">门派</span>
            {factionTabs.map((faction) => {
              const active = faction === activeFaction;
              return (
                <button
                  key={faction}
                  type="button"
                  onClick={() => setActiveFaction(faction)}
                  className={`rounded-sm border px-2.5 py-1 text-[13px] transition ${
                    active
                      ? "border-[#caa75a]/70 bg-[#caa75a]/15 text-[#f4ecd8]"
                      : "border-[#caa75a]/15 bg-[#15140f] text-[#c9c2af] hover:border-[#caa75a]/40 hover:text-[#f4ecd8]"
                  }`}
                >
                  {faction}
                </button>
              );
            })}
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-1.5">
            <span className="mr-1 rounded-sm bg-[#caa75a] px-2 py-1 text-[13px] text-[#1a1812]">分类</span>
            {categoryTabs.map((category) => {
              const active = category === activeCategory;
              return (
                <button
                  key={category}
                  type="button"
                  onClick={() => setActiveCategory(category)}
                  className={`rounded-sm border px-2.5 py-1 text-[13px] transition ${
                    active
                      ? "border-[#caa75a]/70 bg-[#caa75a]/15 text-[#f4ecd8]"
                      : "border-[#caa75a]/15 bg-[#15140f] text-[#c9c2af] hover:border-[#caa75a]/40 hover:text-[#f4ecd8]"
                  }`}
                >
                  {category}
                </button>
              );
            })}
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-1.5">
            <span className="mr-1 rounded-sm bg-[#caa75a] px-2 py-1 text-[13px] text-[#1a1812]">品阶</span>
            {gradeTabs.map((grade) => {
              const active = grade === activeGrade;
              return (
                <button
                  key={grade}
                  type="button"
                  onClick={() => setActiveGrade(grade)}
                  className={`rounded-sm border px-2.5 py-1 text-[13px] transition ${
                    active
                      ? "border-[#caa75a]/70 bg-[#caa75a]/15 text-[#f4ecd8]"
                      : "border-[#caa75a]/15 bg-[#15140f] text-[#c9c2af] hover:border-[#caa75a]/40 hover:text-[#f4ecd8]"
                  }`}
                >
                  {grade}
                </button>
              );
            })}
          </div>
        </div>

        <div className="mt-4 overflow-hidden rounded-2xl border border-[#caa75a]/25 bg-[#15140f] shadow-[0_8px_28px_rgba(0,0,0,0.6)]">
          {visibleRows.length === 0 ? (
            <div className="px-5 py-8 text-center text-[14px] text-[#9a927d]">当前筛选下没有功法</div>
          ) : (
            visibleRows.map((row, rowIndex) => (
              <div
                key={row.label}
                className={`flex items-stretch gap-3 px-3 py-2.5 ${
                  rowIndex === visibleRows.length - 1 ? "" : "border-b border-[#caa75a]/15"
                }`}
              >
                <div className="flex w-[78px] shrink-0 items-center justify-center rounded-md border border-[#caa75a]/20 bg-[#1c1a14] px-1 py-1 text-center font-serif text-[14px] tracking-wider text-[#f4ecd8]">
                  {row.label}
                </div>
                <div className="flex min-w-0 flex-1 flex-wrap gap-2">
                  {row.items.map((item) => {
                    const skill = getSkillById(item.skillId);
                    if (!skill) return null;
                    return (
                      <div
                        key={`${row.label}-${item.skillId}`}
                        className="relative rounded-md border border-[#caa75a]/15 bg-[#1c1a14] px-2 py-1.5"
                      >
                        <SkillChip skill={skill} onEnter={onEnter} onLeave={onLeave} prefix={item.prefix} />
                        <div className="mt-1 flex flex-wrap items-center gap-1 text-[11px] text-[#8f866f]">
                          {item.recommendationSources.map((source) => {
                            const hoverKey = `${item.skillId}-${source.label}`;
                            const colorClass =
                              source.label === "前期推荐"
                                ? "border-[#8fbae7]/20 bg-[#11141b] text-[#b7cbe7]"
                                : source.label === "小米推荐"
                                  ? "border-[#caa75a]/20 bg-[#17140d] text-[#e5cd92]"
                                  : "border-[#8bbf8b]/20 bg-[#111710] text-[#b7dfb1]";
                            return (
                              <span
                                key={hoverKey}
                                className={`rounded-full border px-1.5 py-0.5 ${colorClass}`}
                                onMouseEnter={() => setHoveredReasonSourceKey(hoverKey)}
                                onMouseLeave={() =>
                                  setHoveredReasonSourceKey((current) => (current === hoverKey ? null : current))
                                }
                              >
                                {source.label}
                              </span>
                            );
                          })}
                          {item.buildNames.map((name) => (
                            <span
                              key={`${item.skillId}-${name}`}
                              className="rounded-full border border-[#8fbae7]/20 bg-[#11141b] px-1.5 py-0.5 text-[#b7cbe7]"
                            >
                              {name}
                            </span>
                          ))}
                        </div>
                        {item.recommendationSources.map((source) => {
                          const hoverKey = `${item.skillId}-${source.label}`;
                          if (hoveredReasonSourceKey !== hoverKey || !source.reasons.length) return null;
                          return (
                            <div
                              key={`${hoverKey}-popover`}
                              className="pointer-events-none absolute left-2 top-full z-20 mt-1 w-[320px] max-w-[calc(100vw-48px)] rounded-md border border-[#caa75a]/25 bg-[#14120e] px-3 py-2 text-[12px] leading-5 text-[#d6cfbd] shadow-[0_12px_32px_rgba(0,0,0,0.55)]"
                            >
                              <div className="mb-1 text-[11px] text-[#caa75a]">{source.label}原因</div>
                              {source.reasons.map((reason, reasonIndex) => (
                                <div key={`${hoverKey}-reason-${reasonIndex}`}>{reason}</div>
                              ))}
                            </div>
                          );
                        })}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      </main>
      {hoverNode}
    </div>
  );
}
