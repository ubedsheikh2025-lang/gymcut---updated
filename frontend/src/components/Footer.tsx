"use client";

import { Dumbbell, Github, Twitter } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-neutral-800 bg-black/50 mt-auto">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-neutral-500">
            <Dumbbell className="w-4 h-4" />
            <span className="text-sm">GymCut AI Video Editor — Beta</span>
          </div>

          <div className="flex items-center gap-6 text-sm text-neutral-500">
            <a href="#" className="hover:text-white transition-colors">
              Privacy
            </a>
            <a href="#" className="hover:text-white transition-colors">
              Terms
            </a>
            <a href="#" className="hover:text-white transition-colors">
              Contact
            </a>
          </div>

          <div className="flex items-center gap-3">
            <a
              href="#"
              className="w-8 h-8 rounded-lg bg-neutral-800 flex items-center justify-center text-neutral-500 hover:text-white hover:bg-neutral-700 transition-all"
            >
              <Github className="w-4 h-4" />
            </a>
            <a
              href="#"
              className="w-8 h-8 rounded-lg bg-neutral-800 flex items-center justify-center text-neutral-500 hover:text-white hover:bg-neutral-700 transition-all"
            >
              <Twitter className="w-4 h-4" />
            </a>
          </div>
        </div>

        <p className="text-center text-xs text-neutral-700 mt-6">
          Built with Next.js, FastAPI, FFmpeg, and Google Cloud AI
        </p>
      </div>
    </footer>
  );
}
