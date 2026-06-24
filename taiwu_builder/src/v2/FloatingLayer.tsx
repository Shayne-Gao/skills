import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

type Pos = { x: number; y: number };

type Props = {
  anchor: HTMLElement | null;
  open: boolean;
  width?: number;
  preferred?: "below" | "above" | "auto";
  children: React.ReactNode;
  /** 给外层 wrapper div 加 id，便于外部命中检测（如 hover stable） */
  wrapperId?: string;
  onPointerEnter?: () => void;
  onPointerLeave?: () => void;
};

/**
 * 把内容 portal 到 body，按 anchor 的 boundingClientRect 计算位置。
 * - 优先放在 anchor 下方；不够则放上方
 * - 横向贴 anchor 左边，超出右侧时改为贴 anchor 右边
 * - 高度自适应，超过可用空间内部滚动
 */
export default function FloatingLayer({
  anchor,
  open,
  width = 320,
  preferred = "auto",
  children,
  wrapperId,
  onPointerEnter,
  onPointerLeave,
}: Props) {
  const [pos, setPos] = useState<Pos | null>(null);
  const [maxH, setMaxH] = useState<number>(320);
  const [placement, setPlacement] = useState<"below" | "above">("below");

  useEffect(() => {
    if (!open || !anchor) {
      setPos(null);
      return;
    }
    const compute = () => {
      const r = anchor.getBoundingClientRect();
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      const margin = 12;
      // gap 越小，鼠标从 anchor 移到浮层之间的"空白桥"越小；
      // 同时外层用透明 padding 把这段桥包进浮层的 pointer 区，避免 hover 误触发关闭。
      const gap = 2;

      const spaceBelow = vh - r.bottom - margin;
      const spaceAbove = r.top - margin;
      // preferred 仅作 tie-breaker；优先选可用空间更大的一侧，避免被裁需要内部滚动
      const wantBelow =
        preferred === "above"
          ? false
          : preferred === "below"
          ? true
          : spaceBelow >= spaceAbove;
      const finalPlace: "below" | "above" = wantBelow ? "below" : "above";
      const avail = finalPlace === "below" ? spaceBelow - gap : spaceAbove - gap;

      let x = r.left;
      if (x + width > vw - margin) x = vw - margin - width;
      if (x < margin) x = margin;

      const y = finalPlace === "below" ? r.bottom + gap : r.top - gap; // y 是浮层一端

      setPlacement(finalPlace);
      setPos({ x, y });
      // 允许尽量利用 viewport，多数情况下浮层自然高度 < 这个上限，就不会滚
      setMaxH(Math.max(160, Math.min(vh * 0.88, avail)));
    };
    compute();
    window.addEventListener("scroll", compute, true);
    window.addEventListener("resize", compute);
    return () => {
      window.removeEventListener("scroll", compute, true);
      window.removeEventListener("resize", compute);
    };
  }, [open, anchor, width, preferred]);

  if (!open || !pos) return null;

  // 用透明 padding 把 anchor 到浮层的小段空白桥纳入 pointer 区，
  // 鼠标在这段也算"在浮层上"，不会触发 leave 关闭。
  const bridgePad = 10;
  const wrapperStyle: React.CSSProperties =
    placement === "below"
      ? {
          position: "fixed",
          left: pos.x,
          top: pos.y - bridgePad,
          width,
          paddingTop: bridgePad,
        }
      : {
          position: "fixed",
          left: pos.x,
          bottom: window.innerHeight - pos.y - bridgePad,
          width,
          paddingBottom: bridgePad,
        };
  const innerStyle: React.CSSProperties = {
    maxHeight: maxH,
    overflowY: "auto",
    // 让滚动条藏在浮层内层，不会跑到 padding 桥区域
    overscrollBehavior: "contain",
  };

  return createPortal(
    <div
      id={wrapperId}
      style={{ ...wrapperStyle, zIndex: 200 }}
      onPointerEnter={onPointerEnter}
      onPointerLeave={onPointerLeave}
    >
      <div style={innerStyle}>{children}</div>
    </div>,
    document.body,
  );
}
