import type { SkillRecord } from "@/types";
import {
  ACCENT_RED,
  HOVER_THEME,
  PRACTICE_COLORS,
  SHAPE_COLOR,
  getGradeColor,
  getRouteColor,
} from "./gameColors";
import { diffPair, type DiffSeg } from "./diffText";

type Props = { skill: SkillRecord; practiceMode?: "正练" | "逆练" };

/**
 * 完全还原游戏内 tooltip：
 * - 黑底金边
 * - 标题居中白色 + 右上 id
 * - 元信息行用游戏色（品阶红、路线绿等）
 * - 施展需求、功法属性、心法正/逆练分块
 * - 当同时有正练和逆练时，按字符级 diff 高亮各自独有部分
 */
export default function SkillHoverCard({ skill }: Props) {
  const gradeColor = getGradeColor(skill.grade);
  const routeColor = getRouteColor(skill.route);
  const isSecret = (skill.meta_text || "").includes("不传之秘");

  const zheng = skill.practice_effects.find((p) => p.title.includes("正练"))?.effect;
  const ni = skill.practice_effects.find((p) => p.title.includes("逆练"))?.effect;

  // 同时存在时做 diff；否则整段当 common（无高亮）。
  const { left: zhengSegs, right: niSegs } =
    zheng && ni
      ? diffPair(zheng, ni)
      : {
          left: zheng ? [{ kind: "common" as const, text: zheng }] : [],
          right: ni ? [{ kind: "common" as const, text: ni }] : [],
        };

  // 在 paragraphs 中找“施展需求”行内容
  const cast = findParagraphAfter(skill.paragraphs, "施展需求");
  const hasAttr = skill.bullet_lists.length > 0;

  return (
    <div
      className="rounded-md font-serif text-[14px] leading-snug shadow-[0_18px_40px_rgba(0,0,0,0.55)]"
      style={{
        background: HOVER_THEME.bg,
        border: `1px solid ${HOVER_THEME.border}`,
        color: HOVER_THEME.text,
      }}
    >
      {/* 标题区 */}
      <div className="relative px-3.5 pb-2 pt-2.5">
        <p className="text-center text-[18px] tracking-wider" style={{ color: HOVER_THEME.text }}>
          {skill.name}
        </p>
        <span
          className="absolute right-2.5 top-2.5 text-[11px]"
          style={{ color: HOVER_THEME.subText }}
        >
          id:{skill.id}
        </span>

        <p className="mt-1 text-center text-[13px]">
          {skill.faction ? <span>{skill.faction}</span> : null}
          {skill.grade ? (
            <>
              <span> · </span>
              <span style={{ color: gradeColor }}>{skill.grade}</span>
            </>
          ) : null}
          {skill.route ? (
            <>
              <span> · </span>
              <span style={{ color: routeColor }}>{skill.route}</span>
            </>
          ) : null}
          {skill.category ? (
            <>
              <span> · </span>
              <span>{skill.category}</span>
            </>
          ) : null}
          {skill.shape ? (
            <>
              <span> · </span>
              <span style={{ color: SHAPE_COLOR }}>{skill.shape}</span>
            </>
          ) : null}
          {isSecret ? (
            <>
              <span> · </span>
              <span className="font-bold" style={{ color: ACCENT_RED }}>不传之秘</span>
            </>
          ) : null}
        </p>
      </div>

      {/* 施展需求 */}
      {cast ? (
        <div className="px-3.5 pb-1.5 text-[13.5px]">
          <span className="font-bold">施展需求：</span>
          <span>{cast}</span>
        </div>
      ) : null}

      {/* 功法属性 */}
      {hasAttr ? (
        <div className="px-3.5 pb-2 text-[13.5px]">
          <p className="font-bold">功法属性</p>
          {skill.bullet_lists.map((group, idx) => (
            <ul key={idx} className="mt-0.5">
              {group.map((line, i) => (
                <li key={i} className="leading-snug">· {line}</li>
              ))}
            </ul>
          ))}
        </div>
      ) : null}

      {/* 心法正练 */}
      {zheng ? (
        <div
          className="px-3.5 py-2"
          style={{ borderTop: `1px solid ${HOVER_THEME.divider}` }}
        >
          <p className="font-bold" style={{ color: PRACTICE_COLORS.正练 }}>心法正练</p>
          <p className="mt-0.5 text-[13.5px] leading-snug">
            <DiffText segs={zhengSegs} highlight={PRACTICE_COLORS.正练} />
          </p>
        </div>
      ) : null}

      {/* 心法逆练 */}
      {ni ? (
        <div
          className="px-3.5 py-2"
          style={{ borderTop: `1px solid ${HOVER_THEME.divider}` }}
        >
          <p className="font-bold" style={{ color: PRACTICE_COLORS.逆练 }}>心法逆练</p>
          <p className="mt-0.5 text-[13.5px] leading-snug">
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
          <span
            key={i}
            className="font-bold"
            style={{ color: highlight }}
          >
            {seg.text}
          </span>
        ) : (
          <span key={i}>{seg.text}</span>
        ),
      )}
    </>
  );
}

function findParagraphAfter(paragraphs: string[], key: string) {
  for (const p of paragraphs) {
    if (p.startsWith(key)) {
      // 形如 "施展需求：\n7.2秒 ※ ..."
      const idx = p.indexOf("\n");
      if (idx >= 0) return p.slice(idx + 1).trim();
      // 也可能是 "施展需求：7.2秒..."
      const c = p.indexOf("：");
      if (c >= 0) return p.slice(c + 1).trim();
    }
  }
  return null;
}
