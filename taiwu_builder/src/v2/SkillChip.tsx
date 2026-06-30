import { useRef } from "react";
import type { SkillRecord } from "@/types";
import { getGradeColor } from "./gameColors";

type Props = {
  skill: SkillRecord;
  onEnter: (skillId: string, anchor: HTMLElement, practiceMode?: "正练" | "逆练" | "正/逆") => void;
  onLeave: () => void;
  /** 名字前缀，如推荐组里的 "逆·" */
  prefix?: string;
};

/**
 * 截图风格的功法 chip：
 * - 灰底 + 名字按品阶染色 + 前置 ◇（形状色）
 * - hover anchor 走外部传入的 onEnter / onLeave
 */
export default function SkillChip({ skill, onEnter, onLeave, prefix }: Props) {
  const ref = useRef<HTMLSpanElement>(null);
  const nameColor = getGradeColor(skill.grade);
  const practiceMode =
    prefix === "正·" ? "正练" : prefix === "逆·" ? "逆练" : prefix === "正/逆·" ? "正/逆" : undefined;
  return (
    <span
      ref={ref}
      className="inline-flex items-center gap-1 rounded-sm border border-[#caa75a]/20 bg-[#1c1a14] px-1.5 py-0.5 font-serif text-[14px] leading-tight transition hover:border-[#caa75a]/55 hover:bg-[#2a2618]"
      onMouseEnter={() => ref.current && onEnter(skill.id, ref.current, practiceMode)}
      onMouseLeave={onLeave}
    >
      <span className="text-[#FBFBFB]/85">{skill.shape || "◇"}</span>
      <span style={{ color: nameColor }}>
        {prefix ? <span className="opacity-80">{prefix}</span> : null}
        {skill.name}
      </span>
    </span>
  );
}
