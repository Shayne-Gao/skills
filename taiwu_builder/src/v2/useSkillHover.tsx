import { useEffect, useRef, useState } from "react";
import type { SkillRecord } from "@/types";
import FloatingLayer from "./FloatingLayer";
import SkillHoverCard from "./SkillHoverCard";
import { getSkillById } from "@/utils/taiwuData";

type PracticeHint = "正练" | "逆练" | "正/逆";
type Hover = { skillId: string; anchor: HTMLElement; practiceMode?: PracticeHint } | null;

/**
 * 复用 BuilderPageV2 的 hover 稳定方案：
 * - 全局 mousemove 命中检测 anchor / 浮层（含 16px padding），离开两者才启动关闭计时
 * - 浮层渲染 SkillHoverCard（含正逆练 diff 高亮）
 * 用法：
 *   const { onEnter, onLeave, hoverNode } = useSkillHover();
 *   <span onMouseEnter={(e) => onEnter(skillId, e.currentTarget, "正练")} onMouseLeave={onLeave}>...</span>
 *   {hoverNode}
 */
export function useSkillHover() {
  const [hover, setHover] = useState<Hover>(null);
  const closeTimer = useRef<number | null>(null);

  const cancelClose = () => {
    if (closeTimer.current) {
      window.clearTimeout(closeTimer.current);
      closeTimer.current = null;
    }
  };
  const scheduleClose = () => {
    if (closeTimer.current) window.clearTimeout(closeTimer.current);
    closeTimer.current = window.setTimeout(() => setHover(null), 150);
  };

  const onEnter = (skillId: string, anchor: HTMLElement, practiceMode?: PracticeHint) => {
    cancelClose();
    setHover({ skillId, anchor, practiceMode });
  };
  const onLeave = () => {
    scheduleClose();
  };

  useEffect(() => {
    if (!hover) return;
    const PAD = 16;
    const onMove = (e: MouseEvent) => {
      const x = e.clientX;
      const y = e.clientY;
      const a = hover.anchor.getBoundingClientRect();
      const layer = document.getElementById("v2-skill-hover-layer");
      const lr = layer?.getBoundingClientRect();
      const inRect = (r: DOMRect | undefined) =>
        !!r &&
        x >= r.left - PAD &&
        x <= r.right + PAD &&
        y >= r.top - PAD &&
        y <= r.bottom + PAD;
      if (inRect(a) || inRect(lr)) cancelClose();
      else scheduleClose();
    };
    document.addEventListener("mousemove", onMove);
    return () => document.removeEventListener("mousemove", onMove);
  }, [hover]);

  // ESC 关闭
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setHover(null);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  const skill: SkillRecord | null = hover ? getSkillById(hover.skillId) : null;

  const hoverNode = (
    <FloatingLayer
      anchor={hover?.anchor ?? null}
      open={!!hover && !!skill}
      width={340}
      wrapperId="v2-skill-hover-layer"
      onPointerEnter={cancelClose}
      onPointerLeave={scheduleClose}
    >
      {skill ? <SkillHoverCard skill={skill} practiceMode={hover?.practiceMode} /> : null}
    </FloatingLayer>
  );

  return { onEnter, onLeave, hoverNode };
}
