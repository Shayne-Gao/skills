import { useEffect, useSyncExternalStore } from "react";

export const OWNED_SKILLS_STORAGE_KEY = "taiwu-v2-owned-skills";

type OwnedMap = Record<string, boolean>;

const listeners = new Set<() => void>();
let ownedMapCache: OwnedMap | null = null;

function sanitizeOwnedMap(input: unknown): OwnedMap {
  if (!input || typeof input !== "object") return {};
  return Object.fromEntries(
    Object.entries(input as Record<string, unknown>).filter(
      ([key, value]) => typeof key === "string" && value === true,
    ),
  ) as OwnedMap;
}

function readOwnedMap(): OwnedMap {
  if (ownedMapCache) return ownedMapCache;
  if (typeof window === "undefined") {
    ownedMapCache = {};
    return ownedMapCache;
  }
  try {
    const raw = window.localStorage.getItem(OWNED_SKILLS_STORAGE_KEY);
    ownedMapCache = raw ? sanitizeOwnedMap(JSON.parse(raw)) : {};
  } catch {
    ownedMapCache = {};
  }
  return ownedMapCache;
}

function emitOwnedChange() {
  listeners.forEach((listener) => listener());
}

function writeOwnedMap(next: OwnedMap) {
  ownedMapCache = sanitizeOwnedMap(next);
  if (typeof window !== "undefined") {
    try {
      window.localStorage.setItem(OWNED_SKILLS_STORAGE_KEY, JSON.stringify(ownedMapCache));
    } catch {
      // localStorage 不可用时静默降级
    }
  }
  emitOwnedChange();
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function normalizePracticeMode(mode: "正练" | "逆练" | "正" | "逆") {
  return mode === "正练" || mode === "正" ? "正" : "逆";
}

export function createOwnedSkillKey(skillId: string, practiceMode: "正练" | "逆练" | "正" | "逆") {
  return `${skillId}-${normalizePracticeMode(practiceMode)}`;
}

export function useOwnedSkills() {
  const ownedMap = useSyncExternalStore(subscribe, readOwnedMap, () => ({}));

  useEffect(() => {
    const handleStorage = (event: StorageEvent) => {
      if (event.key !== OWNED_SKILLS_STORAGE_KEY) return;
      ownedMapCache = null;
      emitOwnedChange();
    };
    const syncFromStorage = () => {
      ownedMapCache = null;
      emitOwnedChange();
    };
    syncFromStorage();
    window.addEventListener("storage", handleStorage);
    return () => {
      window.removeEventListener("storage", handleStorage);
    };
  }, []);

  const setOwnedMap = (next: OwnedMap | ((prev: OwnedMap) => OwnedMap)) => {
    const resolved = typeof next === "function" ? next(readOwnedMap()) : next;
    writeOwnedMap(resolved);
  };

  const setOwned = (key: string, owned: boolean) => {
    setOwnedMap((prev) => {
      const next = { ...prev };
      if (owned) next[key] = true;
      else delete next[key];
      return next;
    });
  };

  const toggleOwned = (key: string) => {
    setOwnedMap((prev) => {
      const next = { ...prev };
      if (next[key]) delete next[key];
      else next[key] = true;
      return next;
    });
  };

  const resetOwned = () => writeOwnedMap({});

  return {
    ownedMap,
    setOwnedMap,
    setOwned,
    toggleOwned,
    resetOwned,
  };
}
