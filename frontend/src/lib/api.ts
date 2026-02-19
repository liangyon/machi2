/**
 * Typed API client for the Arcane Depths backend.
 * All requests go through the shared axios instance (lib/axios.ts),
 * which handles auth, 401 redirects, and error normalization centrally.
 *
 * SSE streaming (combat narration) is intentionally kept in lib/sse.ts
 * using raw fetch — axios does not support streaming responses.
 */

import { apiClient } from "@/lib/axios";
import type { GameState, GrimoireEntry, RunStatus, ShrineChoice } from "@/types/game";

// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface MeResponse {
  username: string;
  provider: string;
  email?: string;
  auth_method: string;
  legacy_spellbook: unknown[];
  grimoire_count: number;
}

export interface SignupRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginPasswordRequest {
  email: string;
  password: string;
}

export const authApi = {
  /** Initiate OAuth flow — returns the provider redirect URL */
  login: (provider: "google" | "github") =>
    apiClient
      .post<{ redirect_url: string }>(`/api/auth/login?provider=${provider}`)
      .then((r) => r.data),

  /** Create a new account with username + email + password */
  signup: (body: SignupRequest) =>
    apiClient
      .post<MeResponse>("/api/auth/signup", body)
      .then((r) => r.data),

  /** Log in with email + password */
  loginPassword: (body: LoginPasswordRequest) =>
    apiClient
      .post<MeResponse>("/api/auth/login/password", body)
      .then((r) => r.data),

  me: () => apiClient.get<MeResponse>("/api/auth/me").then((r) => r.data),

  logout: () =>
    apiClient.post<{ message: string }>("/api/auth/logout").then((r) => r.data),
};

// ─── Runs ─────────────────────────────────────────────────────────────────────

export interface StartRunResponse {
  run_id: string;
  state: GameState;
}

export interface RunStateResponse {
  id: string;
  player_class: string;
  state: GameState;
  floor: number;
  status: RunStatus;
}

export interface ExploreResponse {
  room: string;
  event_type: string;
  danger_meter: number;
  action_count: number;
  enemy?: {
    name: string;
    hp: number;
    max_hp: number;
    speed: number;
    active_status_effects: unknown[];
  };
  loot?: { id: string; name: string; tier: string; quantity: number; type: string }[];
  shrine_choices?: { id: number; flavor: string }[];
  shop_items?: unknown[];
}

export interface ShrineChoicesResponse {
  choices: ShrineChoice[];
}

export interface ShrineOutcomeResponse {
  outcome: string;
  effect: string;
  description: string;
  state: Record<string, unknown>;
}

export interface ForgeResponse {
  spell: GrimoireEntry;
}

export interface BossResponse {
  boss: {
    name: string;
    hp: number;
    max_hp: number;
    speed: number;
    active_status_effects: unknown[];
  };
  is_final_boss: boolean;
}

export interface AllocateStatsResponse {
  stat: string;
  points_spent: number;
  state: Record<string, unknown>;
}

export const runsApi = {
  start: (playerClass: string, startingLegacySpells: string[] = []) =>
    apiClient
      .post<StartRunResponse>("/api/run/start", {
        player_class: playerClass,
        starting_legacy_spells: startingLegacySpells,
      })
      .then((r) => r.data),

  getState: (runId: string) =>
    apiClient
      .get<RunStateResponse>(`/api/run/${runId}/state`)
      .then((r) => r.data),

  explore: (runId: string) =>
    apiClient
      .post<ExploreResponse>(`/api/run/${runId}/explore`)
      .then((r) => r.data),

  getShrineChoices: (runId: string) =>
    apiClient
      .post<ShrineChoicesResponse>(`/api/run/${runId}/shrine`)
      .then((r) => r.data),

  chooseShrineOutcome: (runId: string, choiceId: number) =>
    apiClient
      .post<ShrineOutcomeResponse>(`/api/run/${runId}/shrine/choose`, { choice_id: choiceId })
      .then((r) => r.data),

  /**
   * Combat narration streams via SSE — use streamSSE() from lib/sse.ts.
   * This helper just returns the path so callers don't hardcode it.
   */
  combatActionPath: (runId: string) => `/api/run/${runId}/combat/action`,

  forge: (runId: string, ingredients: string[]) =>
    apiClient
      .post<ForgeResponse>(`/api/run/${runId}/forge`, { ingredients })
      .then((r) => r.data),

  boss: (runId: string) =>
    apiClient
      .post<BossResponse>(`/api/run/${runId}/boss`)
      .then((r) => r.data),

  victory: (runId: string, spellToBank?: string) =>
    apiClient
      .post<{ message: string; state: Record<string, unknown> }>(
        `/api/run/${runId}/victory`,
        null,
        spellToBank ? { params: { spell_to_bank: spellToBank } } : undefined
      )
      .then((r) => r.data),

  allocateStats: (runId: string, stat: string, points: number = 1) =>
    apiClient
      .post<AllocateStatsResponse>(`/api/run/${runId}/allocate-stats`, { stat, points })
      .then((r) => r.data),
};

// ─── Grimoire ─────────────────────────────────────────────────────────────────

export interface GrimoireListResponse {
  spells: GrimoireEntry[];
  total: number;
  page: number;
  page_size: number;
}

export const grimoireApi = {
  list: (params: { page?: number; pageSize?: number; name?: string } = {}) =>
    apiClient
      .get<GrimoireListResponse>("/api/grimoire", {
        params: {
          ...(params.page && { page: params.page }),
          ...(params.pageSize && { page_size: params.pageSize }),
          ...(params.name && { name: params.name }),
        },
      })
      .then((r) => r.data),

  get: (ingredientKey: string, variantIndex = 0) =>
    apiClient
      .get<GrimoireEntry>(`/api/grimoire/${ingredientKey}`, {
        params: { variant_index: variantIndex },
      })
      .then((r) => r.data),
};
