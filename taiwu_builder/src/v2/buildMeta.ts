// 五行结构元数据。独立于具体 build 数据，方便 buildIO 等模块复用而避免循环依赖。

import type { BuildSectionKey } from "@/types";

export const buildSections: BuildSectionKey[] = ["内功", "摧破", "轻灵", "护体", "奇窍"];

export const sectionSlotCount: Record<BuildSectionKey, number> = {
  内功: 8,
  摧破: 9,
  轻灵: 7,
  护体: 7,
  奇窍: 10,
};

/**
 * 把功法形状（如 "◇◇◇"）转成默认占用的格子数。
 * 规则：形状里 ◇ 字符的个数就是原型格数；找不到就回退到 1。
 * 精解之后用户会把 occupy 调到 [1, shapeCount] 区间。
 */
export function getShapeBaseCount(shape: string | null | undefined): number {
  if (!shape) return 1;
  const m = shape.match(/◇/g);
  return m ? m.length : 1;
}
