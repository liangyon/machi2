"use client";

import { useEffect, useRef } from "react";
import { useCombatStore } from "@/stores/useCombatStore";

export function NarrativeLog() {
  const narration = useCombatStore((s) => s.narrationBuffer);
  const isStreaming = useCombatStore((s) => s.isStreaming);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [narration]);

  return (
    <div className="flex-1 overflow-y-auto p-4 bg-gray-950 font-serif text-gray-200 leading-relaxed min-h-0">
      <p className="whitespace-pre-wrap">
        {narration}
        {isStreaming && (
          <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-0.5 align-middle" />
        )}
      </p>
      <div ref={bottomRef} />
    </div>
  );
}
