/**
 * Configured Axios instance for Arcane Depths.
 *
 * Interceptors handle:
 *  - Request:  attach credentials / content-type (already defaults via withCredentials)
 *  - Response: normalize errors into a consistent shape
 *              redirect to / on 401 (session expired / not logged in)
 *              redirect to /game on 403 (action not allowed in current state)
 */

import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true, // send session cookies on every request
  headers: {
    "Content-Type": "application/json",
  },
});

// ─── Request interceptor ──────────────────────────────────────────────────────
// Good place to attach a Bearer token if you switch from cookie-based to
// token-based auth later (just pull from a store or localStorage here).
apiClient.interceptors.request.use(
  (config) => {
    // e.g. const token = getAuthToken();
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response interceptor ─────────────────────────────────────────────────────
apiClient.interceptors.response.use(
  // 2xx — pass through
  (response) => response,

  // Non-2xx — normalize and handle globally
  (error) => {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;

      if (status === 401) {
        // Not authenticated — send to home/login.
        // Skip redirect for /api/auth/me so useAuthStore.initAuth() can
        // handle the unauthenticated state gracefully without a redirect loop.
        const url = error.config?.url ?? "";
        if (typeof window !== "undefined" && !url.includes("/api/auth/me")) {
          window.location.href = "/";
        }
      }

      if (status === 403) {
        // Authenticated but action is forbidden in current game state
        console.warn("[API] 403 Forbidden:", error.response?.data);
      }

      // Normalize the error message to the FastAPI `detail` field if present
      const detail = error.response?.data?.detail;
      if (detail) {
        return Promise.reject(new Error(detail));
      }
    }

    return Promise.reject(error);
  }
);
