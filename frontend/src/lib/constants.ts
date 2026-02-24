/** Seniority level color classes — shared across match-card, roles page, etc. */
export const SENIORITY_COLORS: Record<string, string> = {
  entry:
    "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800",
  mid: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800",
  senior:
    "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-900/30 dark:text-purple-300 dark:border-purple-800",
  lead: "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-900/30 dark:text-rose-300 dark:border-rose-800",
  executive:
    "bg-red-50 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800",
};

/** All localStorage keys used by the app. */
export const STORAGE_KEYS = {
  TOKEN: "ct_token",
  USER_ID: "ct_user_id",
  RESUME_ID: "ct_resume_id",
  EMAIL: "ct_email",
  NAME: "ct_name",
  SALARY: "ct_current_salary",
  CACHE_EXPLORE: "ct_cache_explore",
  CACHE_TRANSITIONS: "ct_cache_transitions",
  CACHE_ROADMAP: "ct_cache_roadmap",
  CACHE_DREAM_JOB: "ct_cache_dream_job",
} as const;

/** Clear all session-related data (including cached results) from localStorage. */
export function clearSessionStorage(): void {
  for (const key of Object.values(STORAGE_KEYS)) {
    localStorage.removeItem(key);
  }
}

/** Safe parseInt that returns null instead of NaN. */
export function safeParseInt(value: string): number | null {
  if (!value) return null;
  const parsed = parseInt(value, 10);
  return Number.isNaN(parsed) ? null : parsed;
}

/** Save a result to localStorage cache. */
export function cacheResult<T>(key: string, data: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch {
    // Storage full or unavailable — silently skip
  }
}

/** Load a cached result from localStorage. Returns null if missing or invalid. */
export function loadCachedResult<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}
