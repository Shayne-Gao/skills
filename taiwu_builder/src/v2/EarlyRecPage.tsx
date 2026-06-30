import { useMemo } from "react";
import { curatedRecommendations, getSkillById } from "@/utils/taiwuData";
import SkillChip from "./SkillChip";
import { useSkillHover } from "./useSkillHover";

function getDisplayPrefix(prefix?: string | null) {
  if (prefix === "正·" || prefix === "逆·" || prefix === "正/逆·") return prefix;
  return "正/逆·";
}

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

export default function EarlyRecPage() {
  const { onEnter, onLeave, hoverNode } = useSkillHover();

  const sourceRows = useMemo(
    () =>
      curatedRecommendations.flatMap((tab) =>
        tab.rows.map((row) => ({
          ...row,
          tab_name: tab.tab_name,
        })),
      ),
    [],
  );

  const allRows = useMemo(() => {
    const grouped = new Map<
      string,
      {
        row_id: string;
        skill_ids: string[];
        skill_prefixes: string[];
        recommendation_reason: string;
        source_label: string;
        topic_label: string;
        tab_name: string;
      }
    >();

    sourceRows.forEach((row) => {
      row.skill_ids.forEach((id, index) => {
        const skill = getSkillById(id);
        if (!skill) return;
        const existing = grouped.get(id);
        const prefix = row.skill_prefixes?.[index] ?? null;
        if (!existing) {
          grouped.set(id, {
            row_id: `dedup-${id}`,
            skill_ids: [id],
            skill_prefixes: [prefix ? prefix : "正/逆·"],
            recommendation_reason: row.recommendation_reason,
            source_label: row.source_label ?? "",
            topic_label: `${skill.faction ?? "未知门派"} · ${skill.category ?? "未分类"}`,
            tab_name: row.tab_name,
          });
          return;
        }

        existing.skill_prefixes[0] = mergeDisplayPrefix([existing.skill_prefixes[0], prefix]);

        const reasonParts = new Set(
          existing.recommendation_reason
            .split("；")
            .map((part) => part.trim())
            .filter(Boolean),
        );
        row.recommendation_reason
          .split("；")
          .map((part) => part.trim())
          .filter(Boolean)
          .forEach((part) => reasonParts.add(part));
        existing.recommendation_reason = Array.from(reasonParts).join("；");

        const sourceParts = new Set(
          existing.source_label
            .split(" / ")
            .map((part) => part.trim())
            .filter(Boolean),
        );
        if (row.source_label) sourceParts.add(row.source_label);
        existing.source_label = Array.from(sourceParts).join(" / ");
      });
    });

    return Array.from(grouped.values()).sort((a, b) => Number(a.skill_ids[0]) - Number(b.skill_ids[0]));
  }, [sourceRows]);

  return (
    <div className="min-h-[calc(100vh-100px)] bg-[#0b0b0c] text-[#f4ecd8]">
      <main className="px-5 pb-10 pt-4">
        <div className="flex items-baseline justify-between">
          <h1 className="font-serif text-3xl tracking-wider text-[#f4ecd8]">推荐功法</h1>
          <p className="text-[13px] text-[#9a927d]">
            基于 3 个 build + 原始前期推荐整理 · hover 卡片可查看正逆练对比
          </p>
        </div>
        <div className="mt-3 overflow-hidden rounded-lg border border-[#caa75a]/25 bg-[#15140f] shadow-[0_8px_28px_rgba(0,0,0,0.6)]">
          <div className="grid grid-cols-[minmax(0,1.1fr)_minmax(0,1.5fr)] gap-0 border-b border-[#caa75a]/20 bg-[#1c1a14] px-3 py-2 text-[13px] text-[#caa75a] max-[900px]:grid-cols-1">
            <div className="font-serif">推荐功法</div>
            <div className="font-serif">推荐理由</div>
          </div>
          <div>
            {allRows.map((row, index) => (
              <div
                key={row.row_id}
                className={`grid grid-cols-[minmax(0,1.1fr)_minmax(0,1.5fr)] gap-0 px-3 py-3 max-[900px]:grid-cols-1 ${
                  index === allRows.length - 1 ? "" : "border-b border-[#caa75a]/12"
                }`}
              >
                <div className="pr-4 max-[900px]:pr-0">
                  <div className="mb-1 flex flex-wrap items-center gap-2 text-[11px] text-[#8f866f]">
                    <span>{row.tab_name}</span>
                    {row.source_label ? (
                      <span className="rounded-full border border-[#caa75a]/18 bg-[#1b1913] px-2 py-0.5">
                        {row.source_label}
                      </span>
                    ) : null}
                    {row.topic_label ? <span>{row.topic_label}</span> : null}
                  </div>
                  <div className="flex flex-wrap items-center gap-y-1 text-[14px]">
                    {row.skill_ids.map((id, skillIndex) => {
                      const skill = getSkillById(id);
                      if (!skill) return null;
                      return (
                        <div key={`${row.row_id}-${id}`} className="flex items-center">
                          {skillIndex > 0 ? <span className="px-1.5 text-[#7f7767]">/</span> : null}
                          <SkillChip
                            skill={skill}
                            onEnter={onEnter}
                            onLeave={onLeave}
                            prefix={getDisplayPrefix(row.skill_prefixes?.[skillIndex])}
                          />
                        </div>
                      );
                    })}
                  </div>
                </div>
                <div className="text-[13px] leading-6 text-[#c9c2af] max-[900px]:mt-2">{row.recommendation_reason}</div>
              </div>
            ))}
          </div>
        </div>
      </main>
      {hoverNode}
    </div>
  );
}
