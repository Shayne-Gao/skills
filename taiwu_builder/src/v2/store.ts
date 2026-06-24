import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { BuildRecord, BuildSectionKey, BuildSlot, PracticeMode } from "@/types";
import { createEmptyBuild, defaultBuilds, getSkillById } from "@/utils/taiwuData";
import { clampOccupy } from "./buildIO";
import { getShapeBaseCount } from "./buildMeta";

type V2State = {
  builds: BuildRecord[];
  selectedBuildId: string;
  /** 槽位卡片单格宽度（像素），用于全局调节信息密度。 */
  slotWidth: number;
  setSlotWidth: (px: number) => void;
  selectBuild: (buildId: string) => void;
  createBuild: () => void;
  renameBuild: (buildId: string, name: string) => void;
  setSkill: (p: { buildId: string; section: BuildSectionKey; slotId: string; skillId: string }) => void;
  clearSkill: (p: { buildId: string; section: BuildSectionKey; slotId: string }) => void;
  togglePractice: (p: { buildId: string; section: BuildSectionKey; slotId: string }) => void;
  /** 精解一格：occupy - 1（下限 1）。 */
  refineSkill: (p: { buildId: string; section: BuildSectionKey; slotId: string }) => void;
  /** 还原一格：occupy + 1（上限 shape 原型）。 */
  unrefineSkill: (p: { buildId: string; section: BuildSectionKey; slotId: string }) => void;
};

function patch(builds: BuildRecord[], id: string, fn: (b: BuildRecord) => BuildRecord) {
  return builds.map((b) => (b.id === id ? fn(b) : b));
}

function mapSlot(
  builds: BuildRecord[],
  buildId: string,
  section: BuildSectionKey,
  slotId: string,
  update: (slot: BuildSlot) => BuildSlot,
) {
  return patch(builds, buildId, (b) => ({
    ...b,
    sections: {
      ...b.sections,
      [section]: b.sections[section].map((slot) => (slot.slotId === slotId ? update(slot) : slot)),
    },
  }));
}

function getOccupyBase(skillId: string | null) {
  if (!skillId) return 1;
  return getShapeBaseCount(getSkillById(skillId)?.shape);
}

export const useV2Store = create<V2State>()(
  persist(
    (set) => ({
      builds: defaultBuilds,
      selectedBuildId: defaultBuilds[0].id,
      slotWidth: 80,
      setSlotWidth: (px) => set({ slotWidth: Math.max(40, Math.min(160, Math.round(px))) }),
      selectBuild: (buildId) => set({ selectedBuildId: buildId }),
      createBuild: () =>
        set((s) => {
          const b = createEmptyBuild();
          return { builds: [...s.builds, b], selectedBuildId: b.id };
        }),
      renameBuild: (buildId, name) =>
        set((s) => ({
          builds: patch(s.builds, buildId, (b) => ({ ...b, name: name.trim() || b.name })),
        })),
      setSkill: ({ buildId, section, slotId, skillId }) =>
        set((s) => ({
          builds: mapSlot(s.builds, buildId, section, slotId, (slot) => ({
            ...slot,
            skillId,
            // 新选入功法时按 shape 默认全额占；用户后续点「精解 -1」缩减。
            occupy: getOccupyBase(skillId),
          })),
        })),
      clearSkill: ({ buildId, section, slotId }) =>
        set((s) => ({
          builds: mapSlot(s.builds, buildId, section, slotId, (slot) => ({
            ...slot,
            skillId: null,
            occupy: undefined,
          })),
        })),
      togglePractice: ({ buildId, section, slotId }) =>
        set((s) => ({
          builds: mapSlot(s.builds, buildId, section, slotId, (slot) => ({
            ...slot,
            practiceMode: (slot.practiceMode === "正练" ? "逆练" : "正练") as PracticeMode,
          })),
        })),
      refineSkill: ({ buildId, section, slotId }) =>
        set((s) => ({
          builds: mapSlot(s.builds, buildId, section, slotId, (slot) => {
            if (!slot.skillId) return slot;
            const base = getOccupyBase(slot.skillId);
            const cur = slot.occupy ?? base;
            return { ...slot, occupy: clampOccupy(cur - 1, base) };
          }),
        })),
      unrefineSkill: ({ buildId, section, slotId }) =>
        set((s) => ({
          builds: mapSlot(s.builds, buildId, section, slotId, (slot) => {
            if (!slot.skillId) return slot;
            const base = getOccupyBase(slot.skillId);
            const cur = slot.occupy ?? base;
            return { ...slot, occupy: clampOccupy(cur + 1, base) };
          }),
        })),
    }),
    {
      name: "taiwu-v2-store",
      version: 5,
      // v5：新增内置 build「直伤阴阳逆剑」。
      // v4：BuildSlot 新增 occupy（精解后实际占用格数）。
      // 策略：内置 build 用最新 defaultBuilds 替换；用户自建 build 按 shape 自动补 occupy。
      migrate: (persisted: any, _from) => {
        if (!persisted || !Array.isArray(persisted.builds)) return persisted;
        const builtinIds = new Set(defaultBuilds.map((b) => b.id));
        const userBuilds = persisted.builds
          .filter((b: BuildRecord) => !builtinIds.has(b.id))
          .map((b: BuildRecord) => ({
            ...b,
            sections: Object.fromEntries(
              Object.entries(b.sections).map(([k, slots]) => [
                k,
                (slots as BuildSlot[]).map((slot) => ({
                  ...slot,
                  occupy: slot.skillId ? slot.occupy ?? getOccupyBase(slot.skillId) : undefined,
                })),
              ]),
            ) as BuildRecord["sections"],
          }));
        return {
          ...persisted,
          builds: [...defaultBuilds, ...userBuilds],
        };
      },
    },
  ),
);
