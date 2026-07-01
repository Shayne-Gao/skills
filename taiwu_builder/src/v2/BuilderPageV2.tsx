import { useEffect, useMemo, useRef, useState } from "react";
import type { BuildRecord, BuildSectionKey, BuildSlot } from "@/types";
import { buildSections, getSkillById } from "@/utils/taiwuData";
import { getShapeBaseCount } from "./buildMeta";
import { compactBuild, stringifyBuild } from "./buildIO";
import { useV2Store } from "./store";
import FloatingLayer from "./FloatingLayer";
import SkillHoverCard from "./SkillHoverCard";
import SkillPickerModal from "./SkillPickerModal";
import { ACCENT_RED, HOVER_THEME, PRACTICE_COLORS, getGradeColor } from "./gameColors";
import { createOwnedSkillKey, useOwnedSkills } from "./ownedSkills";

type ActiveMenu = {
  slotId: string;
  section: BuildSectionKey;
  anchor: HTMLElement;
} | null;

type ActiveHover = {
  slotId: string;
  anchor: HTMLElement;
} | null;

const SECTION_ICONS: Record<BuildSectionKey, string> = {
  内功: "内",
  摧破: "摧",
  轻灵: "轻",
  护体: "护",
  奇窍: "奇",
};

export default function BuilderPageV2() {
  const builds = useV2Store((s) => s.builds);
  const selectedBuildId = useV2Store((s) => s.selectedBuildId);
  const selectBuild = useV2Store((s) => s.selectBuild);
  const createBuild = useV2Store((s) => s.createBuild);
  const renameBuild = useV2Store((s) => s.renameBuild);
  const setSkill = useV2Store((s) => s.setSkill);
  const clearSkill = useV2Store((s) => s.clearSkill);
  const togglePractice = useV2Store((s) => s.togglePractice);
  const refineSkill = useV2Store((s) => s.refineSkill);
  const unrefineSkill = useV2Store((s) => s.unrefineSkill);
  const slotWidth = useV2Store((s) => s.slotWidth);
  const setSlotWidth = useV2Store((s) => s.setSlotWidth);

  const build = useMemo(() => builds.find((b) => b.id === selectedBuildId) ?? builds[0], [builds, selectedBuildId]);

  const [menu, setMenu] = useState<ActiveMenu>(null);
  const [hover, setHover] = useState<ActiveHover>(null);
  const [picker, setPicker] = useState<{ slotId: string; section: BuildSectionKey } | null>(null);
  const [copyHint, setCopyHint] = useState<"idle" | "ok" | "fail">("idle");
  const hoverCloseTimerRef = useRef<number | null>(null);
  const { ownedMap } = useOwnedSkills();

  // 点击其他地方关闭操作菜单
  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (!menu) return;
      const target = e.target as Node;
      if (menu.anchor.contains(target)) return;
      const layer = document.getElementById("v2-action-menu");
      if (layer && layer.contains(target)) return;
      setMenu(null);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [menu]);

  // ESC 关闭一切
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setMenu(null);
        setHover(null);
        setPicker(null);
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  const openPicker = (section: BuildSectionKey, slotId: string) => {
    setMenu(null);
    setHover(null);
    setPicker({ section, slotId });
  };

  // 复制当前 build 的 JSON 到剪贴板
  const handleCopyJSON = async () => {
    if (!build) return;
    const payload = stringifyBuild(compactBuild(build));
    try {
      await navigator.clipboard.writeText(payload);
      setCopyHint("ok");
    } catch {
      // 兜底：用 execCommand 同步路径
      const ta = document.createElement("textarea");
      ta.value = payload;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand("copy");
        setCopyHint("ok");
      } catch {
        setCopyHint("fail");
      }
      document.body.removeChild(ta);
    }
    window.setTimeout(() => setCopyHint("idle"), 1600);
  };

  const handlePick = (skillId: string) => {
    if (!picker || !build) return;
    setSkill({ buildId: build.id, section: picker.section, slotId: picker.slotId, skillId });
  };

  const scheduleHoverClose = () => {
    if (hoverCloseTimerRef.current) window.clearTimeout(hoverCloseTimerRef.current);
    // 短延迟 + padding 桥配合：进入浮层方向不会误关，离开方向也不会粘住
    hoverCloseTimerRef.current = window.setTimeout(() => setHover(null), 150);
  };
  const cancelHoverClose = () => {
    if (hoverCloseTimerRef.current) {
      window.clearTimeout(hoverCloseTimerRef.current);
      hoverCloseTimerRef.current = null;
    }
  };

  // 全局 hover 稳定：只要鼠标在 anchor 或浮层矩形（含 padding 桥）内，就保持打开；
  // 完全离开两个区域时才启动关闭计时。比依赖 mouseEnter/Leave 链路更稳。
  useEffect(() => {
    if (!hover) return;
    const HOVER_PAD = 16; // 包容半径，鼠标距任意一个矩形 16px 内都算"在"
    const onMove = (e: MouseEvent) => {
      const x = e.clientX;
      const y = e.clientY;
      const anchorRect = hover.anchor.getBoundingClientRect();
      const layer = document.getElementById("v2-hover-layer");
      const layerRect = layer?.getBoundingClientRect();
      const inRect = (r: DOMRect | undefined) =>
        !!r &&
        x >= r.left - HOVER_PAD &&
        x <= r.right + HOVER_PAD &&
        y >= r.top - HOVER_PAD &&
        y <= r.bottom + HOVER_PAD;
      if (inRect(anchorRect) || inRect(layerRect)) {
        cancelHoverClose();
      } else {
        scheduleHoverClose();
      }
    };
    document.addEventListener("mousemove", onMove);
    return () => document.removeEventListener("mousemove", onMove);
  }, [hover]);

  if (!build) return null;

  const filledTotal = buildSections.reduce(
    (acc, sec) => acc + build.sections[sec].filter((s) => s.skillId).length,
    0,
  );
  const slotTotal = buildSections.reduce((acc, sec) => acc + build.sections[sec].length, 0);

  return (
    <div className="min-h-screen bg-[#0b0b0c] text-[#f4ecd8]">
      {/* Build tab 条（原侧边栏挪到顶部，腾出宽度） */}
      <div className="border-b border-[#caa75a]/15 bg-[#1c1a14]/90 px-5 py-2.5 backdrop-blur">
        <div className="flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-[12px] tracking-[0.2em] text-[#c9c2af]/70">BUILD 册</span>
          {builds.map((b) => {
            const active = b.id === build.id;
            return (
              <button
                key={b.id}
                onClick={() => selectBuild(b.id)}
                className={`group shrink-0 rounded-md border px-3 py-1.5 text-left transition ${
                  active
                    ? "border-[#caa75a]/60 bg-[#2a2618]"
                    : "border-[#caa75a]/15 bg-[#15140f]/60 hover:bg-[#22201a]"
                }`}
                title={b.theme}
              >
                <span className="font-serif text-[15px] text-[#f4ecd8]">{b.name}</span>
              </button>
            );
          })}
          <button
            onClick={createBuild}
            className="shrink-0 rounded-md border border-[#caa75a]/20 bg-[#15140f]/60 px-3 py-1.5 text-[13px] text-[#c9c2af] hover:bg-[#22201a]"
          >
            + 新建
          </button>
          <button
            onClick={handleCopyJSON}
            className="shrink-0 rounded-md border border-[#caa75a]/60 bg-[#caa75a]/90 px-3 py-1.5 text-[13px] text-[#1a1812] hover:bg-[#caa75a]"
            title="复制当前 Build 的 JSON 到剪贴板"
          >
            {copyHint === "ok" ? "✓ 已复制" : copyHint === "fail" ? "× 复制失败" : "⧉ 复制 JSON"}
          </button>

          {/* 全局：单格宽度滑块 */}
          <label className="ml-auto flex shrink-0 items-center gap-2 text-[12px] text-[#c9c2af]">
            <span className="tracking-[0.15em] text-[#c9c2af]/70">单格宽度</span>
            <input
              type="range"
              min={40}
              max={160}
              step={2}
              value={slotWidth}
              onChange={(e) => setSlotWidth(Number(e.target.value))}
              className="h-1 w-32 cursor-pointer accent-[#caa75a]"
            />
            <span className="w-10 text-right tabular-nums text-[#f4ecd8]">{slotWidth}px</span>
          </label>
        </div>
      </div>

      {/* 主区 */}
      <main className="px-5 pb-6 pt-4">
        {/* 标题区 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <input
              value={build.name}
              onChange={(e) => renameBuild(build.id, e.target.value)}
              className="bg-transparent font-serif text-3xl tracking-wider text-[#f4ecd8] outline-none focus:underline"
            />
            <span className="rounded-full border border-[#caa75a]/30 bg-[#15140f]/70 px-3 py-1 text-[13px] text-[#c9c2af]">
              {filledTotal}/{slotTotal} 已配置
            </span>
          </div>
          <p className="text-[13px] text-[#9a927d]">{build.theme}</p>
        </div>

        {/* 五行结构槽位 */}
        <div className="mt-4 overflow-hidden rounded-2xl border border-[#caa75a]/25 bg-[#15140f] shadow-[0_8px_28px_rgba(0,0,0,0.6)]">
          {buildSections.map((section, idx) => (
            <SectionRow
              key={section}
              section={section}
              slots={build.sections[section]}
              ownedMap={ownedMap}
              slotWidth={slotWidth}
              isLast={idx === buildSections.length - 1}
              onEmptyClick={(slotId) => openPicker(section, slotId)}
              onSlotClick={(slot, anchor) => {
                if (!slot.skillId) {
                  openPicker(section, slot.slotId);
                  return;
                }
                setHover(null);
                setMenu({ slotId: slot.slotId, section, anchor });
              }}
              onSlotEnter={(slot, anchor) => {
                cancelHoverClose();
                if (slot.skillId && (!menu || menu.slotId !== slot.slotId)) {
                  setHover({ slotId: slot.slotId, anchor });
                }
              }}
              onSlotLeave={scheduleHoverClose}
              activeSlotId={menu?.slotId ?? null}
            />
          ))}
        </div>

        <p className="mt-3 text-[13px] text-[#9a927d]">
          悬停查看效果 · 点击卡片管理 · 点击空位选取功法 · ESC 关闭浮层
        </p>

        {/* 门派采购清单 */}
        <ShoppingList build={build} />
      </main>

      {/* hover 提示卡 */}
      <FloatingLayer
        anchor={hover?.anchor ?? null}
        open={!!hover && !menu}
        width={320}
        wrapperId="v2-hover-layer"
        onPointerEnter={cancelHoverClose}
        onPointerLeave={scheduleHoverClose}
      >
        {hover
          ? (() => {
              const slot = findSlot(build, hover.slotId);
              const sk = slot ? getSkillById(slot.skillId) : null;
              return slot && sk ? <SkillHoverCard skill={sk} practiceMode={slot.practiceMode} /> : null;
            })()
          : null}
      </FloatingLayer>

      {/* 操作菜单 */}
      <FloatingLayer anchor={menu?.anchor ?? null} open={!!menu} width={240}>
        {menu
          ? (() => {
              const slot = findSlot(build, menu.slotId);
              if (!slot) return null;
              const sk = getSkillById(slot.skillId);
              const baseOccupy = getShapeBaseCount(sk?.shape);
              const curOccupy = slot.occupy ?? baseOccupy;
              const canRefine = curOccupy > 1;
              const canUnrefine = curOccupy < baseOccupy;
              return (
                <div
                  id="v2-action-menu"
                  className="overflow-hidden rounded-md text-sm shadow-[0_18px_40px_rgba(0,0,0,0.55)]"
                  style={{
                    background: HOVER_THEME.bg,
                    border: `1px solid ${HOVER_THEME.border}`,
                    color: HOVER_THEME.text,
                  }}
                >
                  <button
                    className="block w-full px-3 py-2 text-left hover:bg-white/5"
                    onClick={() => {
                      togglePractice({ buildId: build.id, section: menu.section, slotId: menu.slotId });
                      setMenu(null);
                    }}
                  >
                    切换为{" "}
                    <span
                      style={{
                        color:
                          PRACTICE_COLORS[slot.practiceMode === "正练" ? "逆练" : "正练"],
                      }}
                    >
                      {slot.practiceMode === "正练" ? "逆练" : "正练"}
                    </span>
                  </button>
                  {baseOccupy > 1 ? (
                    <>
                      <button
                        disabled={!canRefine}
                        className="block w-full px-3 py-2 text-left hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-40"
                        style={{ borderTop: `1px solid ${HOVER_THEME.divider}` }}
                        onClick={() => {
                          refineSkill({ buildId: build.id, section: menu.section, slotId: menu.slotId });
                        }}
                      >
                        精解 -1 格
                        <span className="ml-2 text-[11px]" style={{ color: HOVER_THEME.subText }}>
                          ({curOccupy} → {Math.max(1, curOccupy - 1)} / 原型 {baseOccupy})
                        </span>
                      </button>
                      <button
                        disabled={!canUnrefine}
                        className="block w-full px-3 py-2 text-left hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-40"
                        style={{ borderTop: `1px solid ${HOVER_THEME.divider}` }}
                        onClick={() => {
                          unrefineSkill({ buildId: build.id, section: menu.section, slotId: menu.slotId });
                        }}
                      >
                        还原 +1 格
                        <span className="ml-2 text-[11px]" style={{ color: HOVER_THEME.subText }}>
                          ({curOccupy} → {Math.min(baseOccupy, curOccupy + 1)})
                        </span>
                      </button>
                    </>
                  ) : null}
                  <button
                    className="block w-full px-3 py-2 text-left hover:bg-white/5"
                    style={{ borderTop: `1px solid ${HOVER_THEME.divider}` }}
                    onClick={() => openPicker(menu.section, menu.slotId)}
                  >
                    替换功法
                  </button>
                  <button
                    className="block w-full px-3 py-2 text-left hover:bg-white/5"
                    style={{
                      borderTop: `1px solid ${HOVER_THEME.divider}`,
                      color: ACCENT_RED,
                    }}
                    onClick={() => {
                      clearSkill({ buildId: build.id, section: menu.section, slotId: menu.slotId });
                      setMenu(null);
                    }}
                  >
                    清空槽位
                  </button>
                </div>
              );
            })()
          : null}
      </FloatingLayer>

      {/* 选功法 Modal */}
      <SkillPickerModal
        open={!!picker}
        section={picker?.section ?? "内功"}
        currentSkillId={
          picker
            ? findSlot(build, picker.slotId)?.skillId ?? null
            : null
        }
        onPick={handlePick}
        onClose={() => setPicker(null)}
      />
    </div>
  );
}

function findSlot(build: ReturnType<typeof useV2Store.getState>["builds"][number], slotId: string) {
  for (const sec of buildSections) {
    const found = build.sections[sec].find((s) => s.slotId === slotId);
    if (found) return found;
  }
  return null;
}

function SectionRow({
  section,
  slots,
  ownedMap,
  slotWidth,
  isLast,
  onEmptyClick,
  onSlotClick,
  onSlotEnter,
  onSlotLeave,
  activeSlotId,
}: {
  section: BuildSectionKey;
  slots: BuildSlot[];
  ownedMap: Record<string, boolean>;
  slotWidth: number;
  isLast: boolean;
  onEmptyClick: (slotId: string) => void;
  onSlotClick: (slot: BuildSlot, anchor: HTMLElement) => void;
  onSlotEnter: (slot: BuildSlot, anchor: HTMLElement) => void;
  onSlotLeave: () => void;
  activeSlotId: string | null;
}) {
  // 计算每段渲染的列跨度。
  //
  // 关键语义（修正 bug）：
  //   - 非空槽位 occupy=N 意味着这张卡"想"占 N 列；
  //   - 但实际只能扩张到后续连续的空槽上，不能吞掉后面已经填了功法的槽位；
  //   - 也不能超出 section 总长。
  //
  // 例：[A(occupy=3), B, C, ., ., .] → A 实际只占 1 格（后面紧邻 B），不能吃 B/C。
  //     [A(occupy=3), ., ., ., B]   → A 实际占 3 格（吃掉两个空格）。
  const segments = useMemo(() => {
    const out: Array<{ slot: BuildSlot; span: number }> = [];
    let i = 0;
    while (i < slots.length) {
      const slot = slots[i];
      if (slot.skillId) {
        const wanted = slot.occupy ?? 1;
        // 数后续连续空槽数
        let trailingEmpty = 0;
        for (let j = i + 1; j < slots.length; j++) {
          if (slots[j].skillId) break;
          trailingEmpty++;
        }
        // 实际跨度 = min(wanted, 1 + 后续连续空槽)
        const span = Math.max(1, Math.min(wanted, 1 + trailingEmpty));
        out.push({ slot, span });
        i += span;
      } else {
        out.push({ slot, span: 1 });
        i += 1;
      }
    }
    return out;
  }, [slots]);

  const filledCount = slots.filter((s) => s.skillId).length;

  return (
    <div
      className={`flex items-stretch gap-2 px-2 py-2 ${isLast ? "" : "border-b border-[#caa75a]/15"}`}
    >
      {/* 分类标识 */}
      <div className="flex w-[58px] shrink-0 flex-col items-center justify-center rounded-lg bg-[#1c1a14] px-1 py-2 border border-[#caa75a]/20">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#caa75a] font-serif text-[15px] text-[#1a1812]">
          {SECTION_ICONS[section]}
        </div>
        <p className="mt-1 text-[12px] text-[#f4ecd8]">{section}</p>
        <p className="text-[11px] text-[#9a927d]">{filledCount}/{slots.length}</p>
      </div>

      {/* 槽位列：每个槽位固定窄宽，配合精解宽卡跨列 */}
      <div
        className="grid min-w-0 flex-1 gap-1.5"
        style={{
          // 单格宽度由全局滑块控制，宽卡通过 gridColumn span 自然拉伸
          gridTemplateColumns: `repeat(${slots.length}, minmax(0, ${slotWidth}px))`,
        }}
      >
        {segments.map(({ slot, span }) => (
          <SlotCell
            key={slot.slotId}
            slot={slot}
            span={span}
            active={activeSlotId === slot.slotId}
            owned={!!(slot.skillId && ownedMap[createOwnedSkillKey(slot.skillId, slot.practiceMode)])}
            onClick={(anchor) => onSlotClick(slot, anchor)}
            onEnter={(anchor) => onSlotEnter(slot, anchor)}
            onLeave={onSlotLeave}
            onEmpty={() => onEmptyClick(slot.slotId)}
          />
        ))}
      </div>
    </div>
  );
}

function SlotCell({
  slot,
  span,
  active,
  owned,
  onClick,
  onEnter,
  onLeave,
  onEmpty,
}: {
  slot: BuildSlot;
  span: number;
  active: boolean;
  owned: boolean;
  onClick: (anchor: HTMLElement) => void;
  onEnter: (anchor: HTMLElement) => void;
  onLeave: () => void;
  onEmpty: () => void;
}) {
  const ref = useRef<HTMLButtonElement>(null);
  const skill = getSkillById(slot.skillId);

  if (!skill) {
    return (
      <button
        ref={ref}
        type="button"
        onClick={onEmpty}
        style={{ gridColumn: `span ${span}` }}
        className="flex h-[80px] items-center justify-center rounded-md border border-dashed border-[#caa75a]/30 bg-[#15140f]/40 text-[15px] text-[#caa75a]/80 transition hover:border-[#caa75a]/60 hover:bg-[#1c1a14]"
      >
        +
      </button>
    );
  }

  const nameColor = getGradeColor(skill.grade);
  const practiceColor = PRACTICE_COLORS[slot.practiceMode];
  const isSecret = (skill.meta_text || "").includes("不传之秘");
  const baseOccupy = getShapeBaseCount(skill.shape);
  const occupy = slot.occupy ?? baseOccupy;
  const refined = occupy < baseOccupy;

  return (
    <button
      ref={ref}
      type="button"
      onClick={() => ref.current && onClick(ref.current)}
      onMouseEnter={() => ref.current && onEnter(ref.current)}
      onMouseLeave={onLeave}
      onFocus={() => ref.current && onEnter(ref.current)}
      onBlur={onLeave}
      className={`group relative h-[80px] overflow-hidden rounded-md border px-1.5 py-1.5 text-left transition ${
        active ? "ring-2" : ""
      }`}
      style={{
        gridColumn: `span ${span}`,
        background: HOVER_THEME.bg,
        borderColor: active ? HOVER_THEME.border : "rgba(202,167,90,0.35)",
        color: HOVER_THEME.text,
        boxShadow: active
          ? `0 0 0 1px ${HOVER_THEME.border}, 0 6px 14px rgba(0,0,0,0.35)`
          : "0 2px 5px rgba(0,0,0,0.22)",
      }}
    >
      <div className="flex h-full flex-col gap-1">
        {/* 单格卡名字允许换 2 行；宽卡（span>1）也允许换行但通常一行就够 */}
        <p
          className="font-serif text-[17px] leading-[1.15]"
          style={{
            color: nameColor,
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
            wordBreak: "break-all",
          }}
        >
          {skill.name}
        </p>
        <div
          className="mt-auto flex items-center justify-between gap-1 text-[12px]"
          style={{ color: HOVER_THEME.subText }}
        >
          <span className="flex items-center gap-1 truncate">
            <span className="tracking-tighter" style={{ color: refined ? "#F4B73B" : "#FBFBFB" }}>
              {"◇".repeat(occupy)}
              {refined ? (
                <span style={{ color: "rgba(255,255,255,0.25)" }}>
                  {"◇".repeat(baseOccupy - occupy)}
                </span>
              ) : null}
            </span>
          </span>
          <span
            className="shrink-0 rounded-sm px-1"
            style={{
              background: "rgba(0,0,0,0.4)",
              border: `1px solid ${practiceColor}`,
              color: practiceColor,
            }}
          >
            {slot.practiceMode === "正练" ? "正" : "逆"}
          </span>
        </div>
      </div>
      {isSecret ? (
        <span
          className="absolute right-0.5 top-0.5 text-[10px]"
          style={{ color: ACCENT_RED }}
          title="不传之秘"
        >
          秘
        </span>
      ) : null}
      {owned ? (
        <span
          className="absolute left-0.5 top-0.5 flex h-4 w-4 items-center justify-center rounded-full border text-[10px]"
          style={{
            borderColor: "#6DB75F",
            background: "rgba(17,35,17,0.9)",
            color: "#9EE08A",
          }}
          title="已获得"
        >
          ✓
        </span>
      ) : null}
    </button>
  );
}

// 品阶排序：神 > 绝 > 超 > 极 > 秘 > 奇 > 上 > 中 > 下 > 凡
const GRADE_ORDER = [
  "神·一品",
  "绝·二品",
  "超·三品",
  "极·四品",
  "秘·五品",
  "奇·六品",
  "上·七品",
  "中·八品",
  "下·九品",
  "凡·十品",
];
const SECTION_ORDER: BuildSectionKey[] = ["内功", "摧破", "轻灵", "护体", "奇窍"];

function ShoppingList({ build }: { build: BuildRecord }) {
  const { ownedMap, toggleOwned } = useOwnedSkills();

  // 把所有已填槽位按门派归类
  const groups = useMemo(() => {
    type Item = {
      slotId: string;
      section: BuildSectionKey;
      skill: NonNullable<ReturnType<typeof getSkillById>>;
      practiceMode: "正练" | "逆练";
    };
    const byFaction = new Map<string, Item[]>();
    for (const sec of SECTION_ORDER) {
      for (const slot of build.sections[sec]) {
        if (!slot.skillId) continue;
        const sk = getSkillById(slot.skillId);
        if (!sk) continue;
        const key = sk.faction?.trim() || "其它 / 无门派";
        const arr = byFaction.get(key) ?? [];
        arr.push({ slotId: slot.slotId, section: sec, skill: sk, practiceMode: slot.practiceMode });
        byFaction.set(key, arr);
      }
    }
    // 每个门派内按 section → grade → name 排序
    const factionList = Array.from(byFaction.entries()).map(([faction, items]) => {
      items.sort((a, b) => {
        const sa = SECTION_ORDER.indexOf(a.section);
        const sb = SECTION_ORDER.indexOf(b.section);
        if (sa !== sb) return sa - sb;
        const ga = GRADE_ORDER.indexOf(a.skill.grade ?? "");
        const gb = GRADE_ORDER.indexOf(b.skill.grade ?? "");
        const gav = ga === -1 ? 99 : ga;
        const gbv = gb === -1 ? 99 : gb;
        // 品阶从低到高（凡·十品 → 神·一品）
        if (gav !== gbv) return gbv - gav;
        return a.skill.name.localeCompare(b.skill.name, "zh-Hans-CN");
      });
      return { faction, items };
    });
    // 门派按条目数倒序，"其它 / 无门派"永远排最后
    factionList.sort((a, b) => {
      if (a.faction === "其它 / 无门派") return 1;
      if (b.faction === "其它 / 无门派") return -1;
      return b.items.length - a.items.length;
    });
    return factionList;
  }, [build]);

  if (groups.length === 0) return null;

  const totalCount = groups.reduce((acc, g) => acc + g.items.length, 0);

  return (
    <section className="mt-6">
      <div className="mb-2 flex items-baseline gap-3">
        <h2 className="font-serif text-lg tracking-wider text-[#f4ecd8]">门派采购清单</h2>
        <span className="text-[13px] text-[#9a927d]">
          共 {groups.length} 个门派 · {totalCount} 个功法
        </span>
      </div>
      <p className="mb-3 text-[13px] text-[#9a927d]">
        按门派归类的功法清单，方便一次性去对应门派学/买齐；正逆练已标注，逆练通常需要先正练后转习。
      </p>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {groups.map(({ faction, items }) => (
          <div
            key={faction}
            className="overflow-hidden rounded-xl border border-[#caa75a]/25 bg-[#15140f] shadow-[0_4px_14px_rgba(0,0,0,0.5)]"
          >
            <header className="flex items-center justify-between border-b border-[#caa75a]/20 bg-[#1c1a14] px-3 py-2">
              <span className="font-serif text-[15px] tracking-wider text-[#f4ecd8]">{faction}</span>
              <span className="text-[12px] text-[#c9c2af]">{items.length} 个</span>
            </header>
            <ul className="divide-y divide-[#caa75a]/10">
              {items.map((it) => {
                const nameColor = getGradeColor(it.skill.grade);
                const practiceColor = PRACTICE_COLORS[it.practiceMode];
                const ownedKey = createOwnedSkillKey(it.skill.id, it.practiceMode);
                const checked = !!ownedMap[ownedKey];
                return (
                  <li
                    key={`${it.slotId}-${ownedKey}`}
                    className={`flex items-center gap-2 px-3 py-2 text-[14px] transition ${
                      checked ? "opacity-40" : ""
                    }`}
                  >
                    <input
                      type="checkbox"
                      className="h-4 w-4 shrink-0 accent-[#caa75a]"
                      checked={checked}
                      onChange={() => toggleOwned(ownedKey)}
                      aria-label={`标记 ${it.skill.name} 是否已获得`}
                    />
                    <span
                      className="shrink-0 rounded-sm bg-[#caa75a]/15 px-1.5 py-[2px] text-[11px] text-[#caa75a]"
                      title={`所属：${it.section}`}
                    >
                      {it.skill.category || it.section}
                    </span>
                    <span className="font-serif" style={{ color: nameColor }}>
                      {it.skill.name}
                    </span>
                    {it.skill.grade ? (
                      <span
                        className="ml-auto shrink-0 rounded-sm border px-1.5 py-[2px] text-[11px]"
                        style={{
                          borderColor: nameColor,
                          color: nameColor,
                          background: "rgba(0,0,0,0.35)",
                        }}
                      >
                        {it.skill.grade}
                      </span>
                    ) : null}
                    <span
                      className="shrink-0 rounded-sm px-1.5 py-[2px] text-[11px]"
                      style={{
                        background: "rgba(0,0,0,0.55)",
                        border: `1px solid ${practiceColor}`,
                        color: practiceColor,
                      }}
                    >
                      {it.practiceMode === "正练" ? "正" : "逆"}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
