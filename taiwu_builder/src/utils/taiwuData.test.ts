import { describe, expect, it } from "vitest";
import { createEmptyBuild, defaultBuilds, filterSkills, getSkillById, getSkillSelectableSections } from "@/utils/taiwuData";

describe("taiwuData", () => {
  it("能创建完整的空白 Build 槽位", () => {
    const build = createEmptyBuild();
    expect(build.sections["内功"]).toHaveLength(8);
    expect(build.sections["摧破"]).toHaveLength(8);
    expect(build.sections["轻灵"]).toHaveLength(6);
    expect(build.sections["护体"]).toHaveLength(3);
    expect(build.sections["奇窍"]).toHaveLength(10);
  });

  it("默认示例 Build 至少包含刀剑类摧破", () => {
    const build = defaultBuilds[0];
    const picked = build.sections["摧破"].map((slot) => getSkillById(slot.skillId));
    const categories = picked.map((skill) => skill?.category);
    expect(categories).toContain("刀法");
    expect(categories).toContain("剑法");
  });

  it("能按目标栏位筛出内功", () => {
    const inner = filterSkills("内功", {
      keyword: "罗汉",
      faction: "",
      category: "",
      grade: "",
      route: "",
    });
    expect(inner.some((skill) => skill.name.includes("罗汉"))).toBe(true);
    expect(inner.every((skill) => getSkillSelectableSections(skill).includes("内功"))).toBe(true);
  });
});
