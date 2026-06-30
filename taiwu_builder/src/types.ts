export type PracticeMode = "正练" | "逆练";

export type BuildSectionKey = "内功" | "摧破" | "轻灵" | "护体" | "奇窍";

export type SkillPracticeEffect = {
  title: string;
  effect: string;
};

export type SkillRecord = {
  id: string;
  name: string;
  href?: string;
  faction: string | null;
  grade: string | null;
  route: string | null;
  category: string | null;
  shape: string | null;
  meta_text: string;
  practice_effects: SkillPracticeEffect[];
  paragraphs: string[];
  bullet_lists: string[][];
  raw_text: string;
  raw_html?: string;
};

export type RecommendationGroup = {
  group_id: string;
  martial_category: string;
  recommendation_category: string;
  skill_ids: string[];
  skill_names: string[];
  recommendation_reason: string;
};

export type CuratedRecommendationRow = {
  row_id: string;
  skill_ids: string[];
  recommendation_reason: string;
  skill_prefixes?: Array<string | null>;
  source_label?: string;
  topic_label?: string;
};

export type CuratedRecommendationTab = {
  tab_id: string;
  tab_name: string;
  rows: CuratedRecommendationRow[];
};

export type UserRecommendationItem = {
  skill_id: string;
  skill_name: string;
  practice_hint?: string | null;
  note?: string | null;
};

export type BuildSlot = {
  slotId: string;
  section: BuildSectionKey;
  skillId: string | null;
  practiceMode: PracticeMode;
  /** 这一格功法实际占用的格子数（精解后会比 shape 原型小）。空槽位忽略此字段。 */
  occupy?: number;
  note?: string;
};

export type BuildRecord = {
  id: string;
  name: string;
  theme: string;
  summary: string;
  highlight: string;
  sections: Record<BuildSectionKey, BuildSlot[]>;
};

export type SkillFilterState = {
  keyword: string;
  faction: string;
  category: string;
  grade: string;
  route: string;
};
