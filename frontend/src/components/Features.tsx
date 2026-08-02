"use client";

import { Wand2, Zap, Scissors, Download, Shield, Smartphone } from "lucide-react";

const FEATURES = [
  {
    icon: Wand2,
    title: "AI Highlight Detection",
    description:
      "Automatically finds your best lifts, poses, and action moments using computer vision.",
  },
  {
    icon: Scissors,
    title: "Auto-Editing",
    description:
      "Clips are stitched together with smooth transitions — no timeline dragging needed.",
  },
  {
    icon: Zap,
    title: "Fast Processing",
    description:
      "Most videos are processed in under 3 minutes. Powered by FFmpeg on the backend.",
  },
  {
    icon: Download,
    title: "One-Click Export",
    description:
      "Download your edited video as MP4, ready for Instagram, TikTok, or YouTube.",
  },
  {
    icon: Shield,
    title: "Privacy First",
    description:
      "Your videos are processed on our server and deleted immediately after. Nothing is stored.",
  },
  {
    icon: Smartphone,
    title: "Works on Mobile",
    description:
      "Upload from your phone, tablet, or desktop. Fully responsive design.",
  },
];

export function Features() {
  return (
    <section id="features" className="w-full max-w-5xl mt-24 mb-16">
      <div className="text-center mb-12">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          No Editing Skills? No Problem.
        </h2>
        <p className="text-neutral-400 text-lg max-w-2xl mx-auto">
          Drop your raw gym footage and get a polished highlight reel in minutes.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {FEATURES.map((feature) => {
          const Icon = feature.icon;
          return (
            <div
              key={feature.title}
              className="glass-card p-6 hover:border-neutral-600 transition-all duration-300 group"
            >
              <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center mb-4 group-hover:bg-orange-500/20 transition-colors">
                <Icon className="w-5 h-5 text-orange-500" />
              </div>
              <h3 className="text-white font-semibold mb-2">{feature.title}</h3>
              <p className="text-neutral-500 text-sm leading-relaxed">
                {feature.description}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
