"use client";

/**
 * UserMenu — compact player info + logout button.
 *
 * Drop this into any authenticated page header.
 * Reads from useAuthStore so it stays in sync with session state.
 *
 * Usage:
 *   import { UserMenu } from "@/components/auth/UserMenu";
 *   <UserMenu />
 */

import { useAuthStore } from "@/stores/useAuthStore";

const PROVIDER_BADGE: Record<string, string> = {
  google: "G",
  github: "GH",
  password: "✉",
};

export function UserMenu() {
  const { player, isAuthenticated, logout } = useAuthStore();

  if (!isAuthenticated || !player) return null;

  const badge = PROVIDER_BADGE[player.provider] ?? player.provider.toUpperCase();

  return (
    <div className="flex items-center gap-3">
      {/* Provider badge + username */}
      <div className="flex items-center gap-2">
        <span className="text-xs font-mono bg-gray-800 text-gray-400 px-1.5 py-0.5 rounded">
          {badge}
        </span>
        <span className="text-sm text-gray-300 font-medium">{player.username}</span>
      </div>

      {/* Logout */}
      <button
        onClick={logout}
        className="text-xs text-gray-500 hover:text-red-400 transition-colors px-2 py-1 rounded hover:bg-gray-800"
        aria-label="Log out"
      >
        Sign out
      </button>
    </div>
  );
}
