/**
 * Auth store — tracks the current player session.
 *
 * Supports both OAuth (Google / GitHub) and username/password auth.
 *
 * On app load, call `initAuth()` to hydrate from the backend (/api/auth/me).
 * The axios interceptor in lib/axios.ts already redirects to "/" on 401,
 * so unauthenticated users are handled globally.
 */

import { create } from "zustand";
import { authApi, type MeResponse, type SignupRequest, type LoginPasswordRequest } from "@/lib/api";

interface AuthState {
  player: MeResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  /** Call once on app mount to check if a session cookie exists. */
  initAuth: () => Promise<void>;

  /** Redirect to the OAuth provider login page. */
  loginOAuth: (provider: "google" | "github") => Promise<void>;

  /** Log in with email + password. Throws on failure (caller shows error). */
  loginPassword: (body: LoginPasswordRequest) => Promise<void>;

  /** Create a new account. Throws on failure (caller shows error). */
  signup: (body: SignupRequest) => Promise<void>;

  /** Clear session on backend + wipe local state. */
  logout: () => Promise<void>;

  /** Internal: set player after successful /me fetch. */
  _setPlayer: (player: MeResponse | null) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  player: null,
  isLoading: true,
  isAuthenticated: false,

  _setPlayer: (player) =>
    set({ player, isAuthenticated: player !== null, isLoading: false }),

  initAuth: async () => {
    set({ isLoading: true });
    try {
      const player = await authApi.me();
      get()._setPlayer(player);
    } catch {
      // 401 is handled by the axios interceptor (redirect to "/")
      // Any other error: treat as unauthenticated
      get()._setPlayer(null);
    }
  },

  loginOAuth: async (provider) => {
    try {
      const { redirect_url } = await authApi.login(provider);
      // Full page navigation — the browser follows the OAuth redirect chain
      window.location.href = redirect_url;
    } catch (err) {
      console.error("[auth] OAuth login failed:", err);
      throw err;
    }
  },

  loginPassword: async (body) => {
    const player = await authApi.loginPassword(body);
    get()._setPlayer(player);
    window.location.href = "/game";
  },

  signup: async (body) => {
    const player = await authApi.signup(body);
    get()._setPlayer(player);
    window.location.href = "/game";
  },

  logout: async () => {
    try {
      await authApi.logout();
    } catch {
      // Best-effort — clear local state regardless
    } finally {
      set({ player: null, isAuthenticated: false });
      window.location.href = "/";
    }
  },
}));
