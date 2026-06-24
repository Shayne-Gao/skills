import { useMemo, useState } from "react";
import type { BuildSectionKey, SkillRecord } from "@/types";
import {
  allFactions,
  allGrades,
  allRoutes,
  getSkillSelectableSections,
  skills,
} from "@/utils/taiwuData";
import {
  ACCENT_RED,
  HOVER_THEME,
  PRACTICE_COLORS,
  SHAPE_COLOR,
  getGradeColor,
  getRouteColor,
} from "./gameColors";
import { diffPair, type DiffSeg } from "./diffText";

type Props = {
  open: boolean;
  section: BuildSectionKey;
  currentSkillId: string | null;
  onPick: (skillId: string) => void;
  onClose: () => void;
};

// 选功法 Modal：左侧筛选 / 中间网格列表 / 右侧实时预览
// 视觉对齐游戏：黑底金边 + 功法名按品阶染色
export default function SkillPickerModal({ open, section, currentSkillId, onPick, onClose }: Props) {
  const [keyword, setKeyword] = useState("");
  const [faction, setFaction] = useState("");
  const [grade, setGrade] = useState("");
  const [route, setRoute] = useState("");
  const [previewId, setPreviewId] = useState<string | null>(currentSkillId);

  const candidates = useMemo(() => {
    return skills.filter((s) => {
      if (!getSkillSelectableSections(s).includes(section)) return false;
      if (faction && s.faction !== faction) return false;
      if (grade && s.grade !== grade) return false;
      if (route && s.route !== route) return false;
      if (keyword.trim()) {
        const kw = keyword.trim().toLowerCase();
        const hay = [s.name, s.faction, s.route, s.category].join(" ").toLowerCase();
        if (!hay.includes(kw)) return false;
      }
      return true;
    });
  }, [section, keyword, faction, grade, route]);

  const preview = useMemo<SkillRecord | null>(
    () => candidates.find((s) => s.id === previewId) ?? candidates[0] ?? null,
    [candidates, previewId],
  );

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[150] flex items-center justify-center bg-black/55 p-6 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="flex h-[min(86vh,720px)] w-[min(96vw,1180px)] flex-col overflow-hidden rounded-md shadow-[0_30px_80px_rgba(0,0,0,0.6)]"
        style={{
          background: HOVER_THEME.bg,
          border: `1px solid ${HOVER_THEME.border}`,
          color: HOVER_THEME.text,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <header
          className="flex items-center justify-between px-5 py-3"
          style={{ borderBottom: `1px solid ${HOVER_THEME.divider}` }}
        >
          <div>
            <p className="text-[11px] tracking-[0.18em]" style={{ color: HOVER_THEME.subText }}>
              为「{section}」选择功法
            </p>
            <p className="font-serif text-lg" style={{ color: HOVER_THEME.text }}>
              共 {candidates.length} 个可选
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded px-3 py-1 text-sm hover:bg-white/5"
            style={{ border: `1px solid ${HOVER_THEME.divider}`, color: HOVER_THEME.subText }}
          >
            关闭
          </button>
        </header>

        <div className="flex flex-1 min-h-0">
          {/* 左：筛选 */}
          <aside
            className="w-[200px] shrink-0 space-y-3 p-4 text-sm"
            style={{
              borderRight: `1px solid ${HOVER_THEME.divider}`,
              background: "rgba(255,255,255,0.02)",
            }}
          >
            <div>
              <label
                className="text-[11px] tracking-[0.16em]"
                style={{ color: HOVER_THEME.subText }}
              >
                关键词
              </label>
              <input
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="搜功法 / 门派"
                className="mt-1 w-full rounded px-2 py-1 text-sm outline-none"
                style={{
                  background: "rgba(0,0,0,0.35)",
                  border: `1px solid ${HOVER_THEME.divider}`,
                  color: HOVER_THEME.text,
                }}
              />
            </div>
            <Selector label="门派" value={faction} onChange={setFaction} options={allFactions} />
            <Selector label="品阶" value={grade} onChange={setGrade} options={allGrades} />
            <Selector label="路线" value={route} onChange={setRoute} options={allRoutes} />
            <button
              type="button"
              onClick={() => {
                setKeyword("");
                setFaction("");
                setGrade("");
                setRoute("");
              }}
              className="w-full rounded py-1 text-xs hover:bg-white/5"
              style={{
                border: `1px solid ${HOVER_THEME.divider}`,
                color: HOVER_THEME.subText,
              }}
            >
              清空筛选
            </button>
          </aside>

          {/* 中：列表 */}
          <main className="flex-1 min-w-0 overflow-y-auto p-4">
            <div className="grid grid-cols-[repeat(auto-fill,minmax(150px,1fr))] gap-2">
              {candidates.map((s) => {
                const active = preview?.id === s.id;
                const nameColor = getGradeColor(s.grade);
                const isSecret = (s.meta_text || "").includes("不传之秘");
                return (
                  <button
                    key={s.id}
                    onMouseEnter={() => setPreviewId(s.id)}
                    onClick={() => setPreviewId(s.id)}
                    onDoubleClick={() => {
                      onPick(s.id);
                      onClose();
                    }}
                    className="relative overflow-hidden rounded px-2.5 py-2 text-left transition"
                    style={{
                      background: active ? "rgba(202,167,90,0.08)" : "rgba(0,0,0,0.3)",
                      border: `1px solid ${
                        active ? HOVER_THEME.border : "rgba(202,167,90,0.25)"
                      }`,
                      color: HOVER_THEME.text,
                      boxShadow: active ? `0 0 0 1px ${HOVER_THEME.border}` : "none",
                    }}
                  >
                    <p
                      className="truncate font-serif text-[14px]"
                      style={{ color: nameColor }}
                    >
                      {s.name}
                    </p>
                    <p
                      className="mt-0.5 truncate text-[10px]"
                      style={{ color: HOVER_THEME.subText }}
                    >
                      {[s.grade, s.faction].filter(Boolean).join(" · ")}
                    </p>
                    {isSecret ? (
                      <span
                        className="absolute right-1 top-1 text-[9px]"
                        style={{ color: ACCENT_RED }}
                      >
                        秘
                      </span>
                    ) : null}
                  </button>
                );
              })}
              {candidates.length === 0 ? (
                <p
                  className="col-span-full py-10 text-center text-sm"
                  style={{ color: HOVER_THEME.subText }}
                >
                  没有符合条件的功法
                </p>
              ) : null}
            </div>
          </main>

          {/* 右：预览 */}
          <aside
            className="w-[320px] shrink-0 overflow-y-auto p-4"
            style={{
              borderLeft: `1px solid ${HOVER_THEME.divider}`,
              background: "rgba(255,255,255,0.02)",
            }}
          >
            {preview ? <Preview skill={preview} /> : (
              <p className="text-sm" style={{ color: HOVER_THEME.subText }}>
                把鼠标移到任意功法上查看详情
              </p>
            )}
            <button
              type="button"
              disabled={!preview}
              onClick={() => {
                if (preview) {
                  onPick(preview.id);
                  onClose();
                }
              }}
              className="mt-4 w-full rounded py-2 text-sm font-medium transition disabled:opacity-40"
              style={{
                background: HOVER_THEME.border,
                color: "#1a1408",
              }}
            >
              选用此功法
            </button>
          </aside>
        </div>
      </div>
    </div>
  );
}

function Selector({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <div>
      <label
        className="text-[11px] tracking-[0.16em]"
        style={{ color: HOVER_THEME.subText }}
      >
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded px-2 py-1 text-sm outline-none"
        style={{
          background: "rgba(0,0,0,0.35)",
          border: `1px solid ${HOVER_THEME.divider}`,
          color: HOVER_THEME.text,
        }}
      >
        <option value="" style={{ color: "#000" }}>全部</option>
        {options.map((o) => (
          <option key={o} value={o} style={{ color: "#000" }}>
            {o}
          </option>
        ))}
      </select>
    </div>
  );
}

function Preview({ skill }: { skill: SkillRecord }) {
  const gradeColor = getGradeColor(skill.grade);
  const routeColor = getRouteColor(skill.route);
  const isSecret = (skill.meta_text || "").includes("不传之秘");
  const zheng = skill.practice_effects.find((p) => p.title.includes("正练"))?.effect;
  const ni = skill.practice_effects.find((p) => p.title.includes("逆练"))?.effect;

  const { left: zhengSegs, right: niSegs } =
    zheng && ni
      ? diffPair(zheng, ni)
      : {
          left: zheng ? [{ kind: "common" as const, text: zheng }] : [],
          right: ni ? [{ kind: "common" as const, text: ni }] : [],
        };

  return (
    <div className="font-serif text-[13px] leading-relaxed">
      <p className="text-center text-[17px] tracking-wider" style={{ color: HOVER_THEME.text }}>
        {skill.name}
      </p>
      <p className="mt-1 text-center text-[12px]">
        {skill.faction ? <span>{skill.faction}</span> : null}
        {skill.grade ? (
          <>
            <span>　</span>
            <span style={{ color: gradeColor }}>{skill.grade}</span>
          </>
        ) : null}
        {skill.route ? (
          <>
            <span>　</span>
            <span style={{ color: routeColor }}>{skill.route}</span>
          </>
        ) : null}
        {skill.category ? (
          <>
            <span>　</span>
            <span>{skill.category}</span>
          </>
        ) : null}
        {skill.shape ? (
          <>
            <span>　</span>
            <span style={{ color: SHAPE_COLOR }}>{skill.shape}</span>
          </>
        ) : null}
        {isSecret ? (
          <>
            <span>　</span>
            <span className="font-bold" style={{ color: ACCENT_RED }}>不传之秘</span>
          </>
        ) : null}
      </p>

      {zheng ? (
        <div className="mt-3 pt-2" style={{ borderTop: `1px solid ${HOVER_THEME.divider}` }}>
          <p className="font-bold" style={{ color: PRACTICE_COLORS.正练 }}>心法正练</p>
          <p className="mt-1 text-[12.5px]">
            <DiffText segs={zhengSegs} highlight={PRACTICE_COLORS.正练} />
          </p>
        </div>
      ) : null}
      {ni ? (
        <div className="mt-2 pt-2" style={{ borderTop: `1px solid ${HOVER_THEME.divider}` }}>
          <p className="font-bold" style={{ color: PRACTICE_COLORS.逆练 }}>心法逆练</p>
          <p className="mt-1 text-[12.5px]">
            <DiffText segs={niSegs} highlight={PRACTICE_COLORS.逆练} />
          </p>
        </div>
      ) : null}
    </div>
  );
}

function DiffText({ segs, highlight }: { segs: DiffSeg[]; highlight: string }) {
  return (
    <>
      {segs.map((seg, i) =>
        seg.kind === "diff" ? (
          <span key={i} className="font-bold" style={{ color: highlight }}>
            {seg.text}
          </span>
        ) : (
          <span key={i}>{seg.text}</span>
        ),
      )}
    </>
  );
}
