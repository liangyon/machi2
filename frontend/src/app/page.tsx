"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useAuthStore } from "@/stores/useAuthStore";
import { AuthModal } from "@/components/auth/AuthModal";

export default function Home() {
  const { player, isLoading, isAuthenticated, initAuth } = useAuthStore();

  // Hydrate auth state from the session cookie on first render
  useEffect(() => {
    initAuth();
  }, [initAuth]);

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-950 text-gray-100 flex items-center justify-center">
        <p className="text-gray-500 animate-pulse">Checking session…</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 flex flex-col items-center justify-center gap-8 p-8">
      <div className="text-center space-y-2">
        <h1 className="text-5xl font-bold tracking-tight text-purple-300">
          Arcane Depths
        </h1>
        <p className="text-gray-400 text-lg">
          A roguelike dungeon crawler powered by LLM spell synthesis
        </p>
      </div>

      {isAuthenticated && player ? (
        /* ── Authenticated: show game nav ── */
        <div className="flex flex-col gap-3 w-full max-w-xs">
          <p className="text-center text-sm text-gray-400">
            Welcome back,{" "}
            <span className="text-purple-300 font-semibold">{player.username}</span>
          </p>
          <Link
            href="/game"
            className="text-center px-6 py-3 rounded-lg bg-purple-700 hover:bg-purple-600 font-semibold text-lg transition-colors"
          >
            ⚔️ New Run
          </Link>
          <Link
            href="/grimoire"
            className="text-center px-6 py-3 rounded-lg bg-gray-800 hover:bg-gray-700 font-semibold transition-colors"
          >
            📖 Grimoire
          </Link>
          <Link
            href="/legacy"
            className="text-center px-6 py-3 rounded-lg bg-gray-800 hover:bg-gray-700 font-semibold transition-colors"
          >
            📚 Legacy Spellbook
          </Link>
        </div>
      ) : (
        /* ── Unauthenticated: show auth modal ── */
        <div className="w-full max-w-sm">
          <p className="text-center text-sm text-gray-500 mb-4">
            Sign in to begin your descent
          </p>
          <AuthModal />
        </div>
      )}
    </main>
  );
}
