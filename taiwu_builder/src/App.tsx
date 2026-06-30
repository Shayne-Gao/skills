import { useState } from "react";
import BuilderPageV2 from "@/v2/BuilderPageV2";
import EarlyRecPage from "@/v2/EarlyRecPage";
import AllSkillsPage from "@/v2/AllSkillsPage";
import FactionShoppingPage from "@/v2/FactionShoppingPage";

type View = "build" | "early" | "shopping" | "all";

const TABS: Array<{ id: View; label: string }> = [
  { id: "build", label: "Build 搭配" },
  { id: "early", label: "前期功法推荐" },
  { id: "shopping", label: "门派购物清单" },
  { id: "all", label: "全部功法一览" },
];

export default function App() {
  const [view, setView] = useState<View>("build");

  return (
    <div className="min-h-screen bg-[#0b0b0c] text-[#f4ecd8]">
      {/* 全局 Header（带页面 tab） */}
      <header className="flex items-center justify-between border-b border-[#caa75a]/25 bg-[#15140f]/95 px-6 py-3 backdrop-blur">
        <div className="flex items-center gap-2">
          <span className="font-serif text-xl tracking-wider text-[#f4ecd8]">太吾绘卷 · Build 搭配器</span>
        </div>
        <nav className="flex items-center gap-1.5">
          {TABS.map((t) => {
            const active = t.id === view;
            return (
              <button
                key={t.id}
                onClick={() => setView(t.id)}
                className={`rounded-md border px-3 py-1.5 text-[14px] transition ${
                  active
                    ? "border-[#caa75a]/70 bg-[#caa75a]/15 text-[#f4ecd8]"
                    : "border-[#caa75a]/15 bg-[#1c1a14] text-[#c9c2af] hover:border-[#caa75a]/40 hover:text-[#f4ecd8]"
                }`}
              >
                {t.label}
              </button>
            );
          })}
        </nav>
      </header>

      {view === "build" ? <BuilderPageV2 /> : null}
      {view === "early" ? <EarlyRecPage /> : null}
      {view === "shopping" ? <FactionShoppingPage /> : null}
      {view === "all" ? <AllSkillsPage /> : null}
    </div>
  );
}
