import { useMemo, useState } from "react";
import { curatedRecommendations, getSkillById } from "@/utils/taiwuData";
import SkillChip from "./SkillChip";
import { useSkillHover } from "./useSkillHover";
export default function EarlyRecPage() {
  const { onEnter, onLeave, hoverNode } = useSkillHover();
  const [activeTabId, setActiveTabId] = useState(curatedRecommendations[0]?.tab_id ?? "");

  const activeTab = useMemo(
    () => curatedRecommendations.find((tab) => tab.tab_id === activeTabId) ?? curatedRecommendations[0] ?? null,
    [activeTabId],
  );

  return (
    <div className="min-h-[calc(100vh-100px)] bg-[#0b0b0c] text-[#f4ecd8]">
      <main className="px-5 pb-10 pt-4">
        <div className="flex items-baseline justify-between">
          <h1 className="font-serif text-3xl tracking-wider text-[#f4ecd8]">前期功法推荐</h1>
          <p className="text-[13px] text-[#9a927d]">
            基于 3 个 build + 原始前期推荐整理 · hover 卡片可查看正逆练对比
          </p>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {curatedRecommendations.map((tab) => {
            const active = tab.tab_id === activeTab?.tab_id;
            return (
              <button
                key={tab.tab_id}
                type="button"
                onClick={() => setActiveTabId(tab.tab_id)}
                className={`rounded-full border px-4 py-1.5 font-serif text-[14px] transition ${
                  active
                    ? "border-[#caa75a] bg-[#caa75a]/16 text-[#f6d79a]"
                    : "border-[#caa75a]/20 bg-[#15140f] text-[#b7af9c] hover:border-[#caa75a]/45 hover:text-[#f4ecd8]"
                }`}
              >
                {tab.tab_name}
              </button>
            );
          })}
        </div>

        <div className="mt-3 overflow-hidden rounded-lg border border-[#caa75a]/25 bg-[#15140f] shadow-[0_8px_28px_rgba(0,0,0,0.6)]">
          <div className="grid grid-cols-[minmax(0,1.1fr)_minmax(0,1.5fr)] gap-0 border-b border-[#caa75a]/20 bg-[#1c1a14] px-3 py-2 text-[13px] text-[#caa75a] max-[900px]:grid-cols-1">
            <div className="font-serif">推荐功法</div>
            <div className="font-serif">推荐理由</div>
          </div>
          <div>
            {activeTab?.rows.map((row, index) => (
              <div
                key={row.row_id}
                className={`grid grid-cols-[minmax(0,1.1fr)_minmax(0,1.5fr)] gap-0 px-3 py-3 max-[900px]:grid-cols-1 ${
                  index === activeTab.rows.length - 1 ? "" : "border-b border-[#caa75a]/12"
                }`}
              >
                <div className="pr-4 max-[900px]:pr-0">
                  <div className="mb-1 flex flex-wrap items-center gap-2 text-[11px] text-[#8f866f]">
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
                            prefix={row.skill_prefixes?.[skillIndex] ?? undefined}
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
