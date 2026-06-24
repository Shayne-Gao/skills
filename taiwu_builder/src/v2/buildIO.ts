// Build 数据态 ↔ 展示态互转。
//
// 数据态（BuildExport）是导入/导出/持久化的紧凑形式：
//   - 只记录非空槽位 [section, indexFrom1, skillId, mode, occupy?]
//   - occupy 表示精解后实际占用的格数；省略 = 按 shape 原型补齐
//   - schema 字段做版本号，便于以后升级
//
// 展示态（BuildRecord）是 UI 使用的全槽位结构：每个 section 都有 sectionSlotCount
// 长度的数组，没填的位用 skillId=null 表示。

import type { BuildRecord, BuildSectionKey, BuildSlot, PracticeMode } from "@/types";
import { buildSections, getShapeBaseCount, sectionSlotCount } from "./buildMeta";

// 紧凑 slot tuple：占用列可选；导出时若与 shape 原型相同，仍写出便于人读。
type SlotTuple =
  | [BuildSectionKey, number, string, PracticeMode]
  | [BuildSectionKey, number, string, PracticeMode, number];

export type BuildExport = {
  schema: "taiwu-build/v1";
  id: string;
  name: string;
  theme?: string;
  summary?: string;
  highlight?: string;
  slots: SlotTuple[];
};

/**
 * 紧凑数据 → 展示态（填满所有槽位，空位置 skillId=null）。
 *
 * occupy 兜底策略：
 *  - 数据里写了就用数据里的；
 *  - 没写则用 lookupShape(skillId) 取出 shape，按 ◇ 个数补齐；
 *  - 仍然取不到默认 1。
 */
export function expandBuild(
  data: BuildExport,
  lookupShape: (skillId: string) => string | null | undefined = () => null,
): BuildRecord {
  const sections = {} as Record<BuildSectionKey, BuildSlot[]>;
  for (const section of buildSections) {
    const count = sectionSlotCount[section];
    sections[section] = Array.from({ length: count }, (_, i) => ({
      slotId: `${section}-${i + 1}`,
      section,
      skillId: null,
      practiceMode: "正练" as PracticeMode,
    }));
  }
  for (const tuple of data.slots) {
    const [section, idx, skillId, mode] = tuple;
    const explicitOccupy = tuple.length === 5 ? tuple[4] : undefined;
    const arr = sections[section];
    if (!arr) continue;
    const slot = arr[idx - 1];
    if (!slot) continue;
    slot.skillId = skillId;
    slot.practiceMode = mode;
    const baseOccupy = getShapeBaseCount(lookupShape(skillId));
    slot.occupy = clampOccupy(explicitOccupy ?? baseOccupy, baseOccupy);
  }
  return {
    id: data.id,
    name: data.name,
    theme: data.theme ?? "",
    summary: data.summary ?? "",
    highlight: data.highlight ?? "",
    sections,
  };
}

/** 展示态 → 紧凑数据（只保留非空槽位，并写出 occupy）。 */
export function compactBuild(record: BuildRecord): BuildExport {
  const slots: SlotTuple[] = [];
  for (const section of buildSections) {
    record.sections[section].forEach((slot, i) => {
      if (!slot.skillId) return;
      const occupy = slot.occupy ?? 1;
      slots.push([section, i + 1, slot.skillId, slot.practiceMode, occupy]);
    });
  }
  return {
    schema: "taiwu-build/v1",
    id: record.id,
    name: record.name,
    theme: record.theme || undefined,
    summary: record.summary || undefined,
    highlight: record.highlight || undefined,
    slots,
  };
}

/** 解析 JSON 字符串为 BuildExport，并做最低限度的校验。 */
export function parseBuildJSON(text: string): BuildExport {
  const obj = JSON.parse(text);
  if (!obj || obj.schema !== "taiwu-build/v1") {
    throw new Error("不是合法的 taiwu-build/v1 JSON");
  }
  if (typeof obj.id !== "string" || typeof obj.name !== "string" || !Array.isArray(obj.slots)) {
    throw new Error("缺少必要字段（id / name / slots）");
  }
  return obj as BuildExport;
}

/** 把 BuildExport 序列化成可读的 JSON 字符串。 */
export function stringifyBuild(data: BuildExport): string {
  return JSON.stringify(data, null, 2);
}

/** 把 occupy 收敛到 [1, base]。 */
export function clampOccupy(value: number, base: number) {
  const max = Math.max(1, base);
  if (!Number.isFinite(value)) return max;
  return Math.min(max, Math.max(1, Math.floor(value)));
}
