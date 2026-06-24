import rawRecommendations from "../../data/parsed/early_recommendations.json";
import curatedRecommendationSource from "../../data/parsed/curated_recommendations.json";
import rawSkills from "../../data/parsed/skills.json";
import bladeDanceData from "../v2/builds/blade-dance.json";
import taijiWuxiaData from "../v2/builds/taiji-wuxia.json";
import yinyangDirectDamageData from "../v2/builds/yinyang-direct-damage.json";
import { expandBuild, type BuildExport } from "../v2/buildIO";
import { buildSections, sectionSlotCount } from "../v2/buildMeta";
import type {
  BuildRecord,
  BuildSectionKey,
  BuildSlot,
  CuratedRecommendationTab,
  PracticeMode,
  RecommendationGroup,
  SkillFilterState,
  SkillRecord,
} from "@/types";

const ATTACK_CATEGORIES = new Set([
  "刀法",
  "剑法",
  "拳掌",
  "指法",
  "腿法",
  "暗器",
  "奇门",
  "长兵",
  "御射",
  "乐器",
  "软兵",
]);

export { buildSections, sectionSlotCount };

export const recommendationData = rawRecommendations.items as RecommendationGroup[];
const curatedRecommendationTabs = curatedRecommendationSource.tabs as CuratedRecommendationTab[];
export const skills = rawSkills.items as SkillRecord[];
export const skillMap = new Map(skills.map((skill) => [skill.id, skill]));

function mapRecommendationTabId(section: string) {
  if (section === "内功") return "internal";
  if (section === "摧破") return "attack";
  if (section === "轻灵") return "movement";
  if (section === "护体" || section === "奇窍") return "special";
  return null;
}

const tabNameMap: Record<string, string> = {
  internal: "内功推荐",
  attack: "摧破推荐",
  movement: "身法推荐",
  special: "绝技推荐",
};

const legacyRecommendationTabs = Object.values(
  recommendationData.reduce<Record<string, CuratedRecommendationTab>>((acc, group) => {
    const tabId = mapRecommendationTabId(group.martial_category);
    if (!tabId) return acc;
    if (!acc[tabId]) {
      acc[tabId] = {
        tab_id: tabId,
        tab_name: tabNameMap[tabId] ?? group.martial_category,
        rows: [],
      };
    }
    acc[tabId].rows.push({
      row_id: `legacy-${group.group_id.replace(/\//g, "-")}`,
      skill_ids: group.skill_ids,
      recommendation_reason: group.recommendation_reason,
      skill_prefixes: group.skill_names.map((name) => {
        const matched = /^([正逆])·/.exec(name);
        return matched ? `${matched[1]}·` : null;
      }),
      source_label: "前期推荐",
      topic_label: group.recommendation_category,
    });
    return acc;
  }, {}),
);

export const curatedRecommendations = curatedRecommendationTabs.map((tab) => {
  const legacyTab = legacyRecommendationTabs.find((item) => item.tab_id === tab.tab_id);
  return {
    ...tab,
    rows: [
      ...tab.rows.map((row) => ({
        ...row,
        source_label: row.source_label ?? "综合整理",
      })),
      ...(legacyTab?.rows ?? []),
    ],
  };
});

const hintedSectionBySkillId = recommendationData.reduce<Record<string, BuildSectionKey>>((acc, group) => {
  if (buildSections.includes(group.martial_category as BuildSectionKey)) {
    group.skill_ids.forEach((id) => {
      acc[id] = group.martial_category as BuildSectionKey;
    });
  }
  return acc;
}, {});

export const allFactions = Array.from(new Set(skills.map((skill) => skill.faction).filter(Boolean))).sort();
export const allRoutes = Array.from(new Set(skills.map((skill) => skill.route).filter(Boolean))).sort();
export const allGrades = Array.from(new Set(skills.map((skill) => skill.grade).filter(Boolean))).sort();
export const allCategories = Array.from(new Set(skills.map((skill) => skill.category).filter(Boolean))).sort();

function createSlots(section: BuildSectionKey, defs: Array<[string | null, PracticeMode]>) {
  const count = sectionSlotCount[section];
  return Array.from({ length: count }, (_, index) => {
    const picked = defs[index];
    const slot: BuildSlot = {
      slotId: `${section}-${index + 1}`,
      section,
      skillId: picked?.[0] ?? null,
      practiceMode: picked?.[1] ?? "正练",
    };
    return slot;
  });
}

export function createEmptyBuild(name = "新建 Build"): BuildRecord {
  return {
    id: `build-${Date.now()}`,
    name,
    theme: "自由搭配",
    summary: "从功法选择页挑选你想尝试的功法，并逐步拼成一套完整套路。",
    highlight: "当前还是空白 Build，适合拿来实验正逆练和不同门派混搭。",
    sections: {
      内功: createSlots("内功", []),
      摧破: createSlots("摧破", []),
      轻灵: createSlots("轻灵", []),
      护体: createSlots("护体", []),
      奇窍: createSlots("奇窍", []),
    },
  };
}

// 内置 build 全部以纯数据 JSON 形式存放在 src/v2/builds/*.json，
// 运行时通过 expandBuild 展开成 UI 用的 BuildRecord。导出时再 compactBuild 回压。
const lookupShape = (skillId: string) => skillMap.get(skillId)?.shape ?? null;
export const defaultBuilds: BuildRecord[] = [
  expandBuild(bladeDanceData as BuildExport, lookupShape),
  expandBuild(taijiWuxiaData as BuildExport, lookupShape),
  expandBuild(yinyangDirectDamageData as BuildExport, lookupShape),
];

export function getSkillById(skillId: string | null | undefined) {
  return skillId ? skillMap.get(skillId) ?? null : null;
}

export function getSkillPrimarySection(skill: SkillRecord): BuildSectionKey | null {
  if (skill.category === "内功") return "内功";
  if (skill.category === "身法") return "轻灵";
  if (ATTACK_CATEGORIES.has(skill.category || "")) return "摧破";
  if (skill.category === "绝技") return hintedSectionBySkillId[skill.id] ?? null;
  return null;
}

export function getSkillSelectableSections(skill: SkillRecord): BuildSectionKey[] {
  const primary = getSkillPrimarySection(skill);
  if (primary) return [primary];
  if (skill.category === "绝技") return ["护体", "奇窍"];
  return [];
}

export function getPracticeEffect(skill: SkillRecord, mode: PracticeMode) {
  const key = mode === "正练" ? "正练" : "逆练";
  return skill.practice_effects.find((effect) => effect.title.includes(key)) ?? null;
}

export function getSkillDisplayTags(skill: SkillRecord) {
  return [skill.faction, skill.grade, skill.route, skill.category].filter(Boolean) as string[];
}

export function getGradeTone(grade: string | null | undefined) {
  if (!grade) {
    return {
      badge: "border-stone-300 bg-stone-100 text-stone-700",
      chip: "border-stone-300 bg-stone-100 text-stone-700",
      glow: "border-stone-200",
    };
  }

  const tier = grade.split("·")[0];
  const tones: Record<string, { badge: string; chip: string; glow: string }> = {
    下: {
      badge: "border-slate-300 bg-slate-50 text-slate-700",
      chip: "border-slate-300 bg-slate-50 text-slate-700",
      glow: "border-slate-200",
    },
    中: {
      badge: "border-emerald-300 bg-emerald-50 text-emerald-800",
      chip: "border-emerald-300 bg-emerald-50 text-emerald-800",
      glow: "border-emerald-200",
    },
    上: {
      badge: "border-sky-300 bg-sky-50 text-sky-800",
      chip: "border-sky-300 bg-sky-50 text-sky-800",
      glow: "border-sky-200",
    },
    奇: {
      badge: "border-amber-300 bg-amber-50 text-amber-900",
      chip: "border-amber-300 bg-amber-50 text-amber-900",
      glow: "border-amber-200",
    },
    秘: {
      badge: "border-fuchsia-300 bg-fuchsia-50 text-fuchsia-800",
      chip: "border-fuchsia-300 bg-fuchsia-50 text-fuchsia-800",
      glow: "border-fuchsia-200",
    },
    极: {
      badge: "border-rose-300 bg-rose-50 text-rose-800",
      chip: "border-rose-300 bg-rose-50 text-rose-800",
      glow: "border-rose-200",
    },
    超: {
      badge: "border-orange-300 bg-orange-50 text-orange-900",
      chip: "border-orange-300 bg-orange-50 text-orange-900",
      glow: "border-orange-200",
    },
    绝: {
      badge: "border-violet-300 bg-violet-50 text-violet-800",
      chip: "border-violet-300 bg-violet-50 text-violet-800",
      glow: "border-violet-200",
    },
    神: {
      badge: "border-yellow-300 bg-yellow-50 text-yellow-900",
      chip: "border-yellow-300 bg-yellow-50 text-yellow-900",
      glow: "border-yellow-200",
    },
  };

  return tones[tier] ?? {
    badge: "border-stone-300 bg-stone-100 text-stone-700",
    chip: "border-stone-300 bg-stone-100 text-stone-700",
    glow: "border-stone-200",
  };
}

export function filterSkills(targetSection: BuildSectionKey, filters: SkillFilterState) {
  const keyword = filters.keyword.trim();
  return skills.filter((skill) => {
    const allowedSections = getSkillSelectableSections(skill);
    if (!allowedSections.includes(targetSection)) return false;
    if (filters.faction && skill.faction !== filters.faction) return false;
    if (filters.category && skill.category !== filters.category) return false;
    if (filters.grade && skill.grade !== filters.grade) return false;
    if (filters.route && skill.route !== filters.route) return false;
    if (!keyword) return true;
    const haystack = [skill.name, skill.faction, skill.route, skill.category, skill.raw_text].join(" ").toLowerCase();
    return haystack.includes(keyword.toLowerCase());
  });
}

export function getRecommendationGroupsForSkill(skillId: string) {
  return recommendationData.filter((group) => group.skill_ids.includes(skillId));
}

export function getSectionSummary(section: BuildSectionKey) {
  const mapping: Record<BuildSectionKey, string> = {
    内功: "管理周转、增伤与减耗，是整套 Build 的内在骨架。",
    摧破: "承担主要输出与控制压力，刀剑乱舞示例重点放在这里。",
    轻灵: "负责位移、抢节奏与额外进攻动作。",
    护体: "补足减伤、化解与站场稳定性。",
    奇窍: "作为增伤、辅助与战斗节奏放大器。",
  };
  return mapping[section];
}
