"use client";

import { Dumbbell } from "lucide-react";

export function Header() {
  return (
    <header className="border-b border-neutral-800 bg-black/50 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
            <Dumbbell className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg">GymCut</span>
            <span className="text-xs text-neutral-500 ml-2 hidden sm:inline">AI Video Editor</span>
          </div>
        </div>

        <nav className="flex items-center gap-4 text-sm text-neutral-400">
          <a href="#features" className="hover:text-white transition-colors hidden sm:block">
            Features
          </a>
          <a href="#how-it-works" className="hover:text-white transition-colors hidden sm:block">
            How It Works
          </a>
          <span className="text-xs bg-neutral-800 px-3 py-1 rounded-full text-neutral-500">
            Beta
          </span>
        </nav>
      </div>
    </header>
  );
}
