"use client";

import { useEffect, useRef } from "react";
import { Loader2, CheckCircle2, Film, Scissors, Wand2 } from "lucide-react";
import { getJobStatus } from "@/lib/api";
import type { JobStatus } from "@/lib/api";

interface ProcessingPanelProps {
  jobId: string;
  onStatusUpdate: (status: JobStatus) => void;
  onError: (message: string) => void;
}

const STATUS_ICONS: Record<string, React.ReactNode> = {
  uploading: <Film className="w-5 h-5" />,
  analyzing: <Wand2 className="w-5 h-5" />,
  editing: <Scissors className="w-5 h-5" />,
  rendering: <Film className="w-5 h-5" />,
};

const STATUS_LABELS: Record<string, string> = {
  uploading: "Uploading video...",
  analyzing: "Analyzing your workout...",
  editing: "Editing highlights together...",
  rendering: "Rendering final video...",
};

export function ProcessingPanel({
  jobId,
  onStatusUpdate,
  onError,
}: ProcessingPanelProps) {
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let cancelled = false;

    const poll = async () => {
      try {
        const status = await getJobStatus(jobId);
        if (cancelled) return;

        onStatusUpdate(status);

        if (status.status === "done" || status.status === "failed") {
          if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
          }
        }
      } catch (err: any) {
        if (!cancelled) {
          onError(err.message || "Connection lost. Please try again.");
        }
      }
    };

    // Poll every 2 seconds
    poll(); // immediate first call
    pollRef.current = setInterval(poll, 2000);

    return () => {
      cancelled = true;
      if (pollRef.current) {
        clearInterval(pollRef.current);
      }
    };
  }, [jobId, onStatusUpdate, onError]);

  return (
    <div className="w-full max-w-lg animate-in">
      <div className="glass-card p-8 text-center space-y-6">
        {/* Spinner */}
        <div className="relative w-24 h-24 mx-auto">
          <div className="absolute inset-0 rounded-full border-4 border-neutral-800" />
          <div className="absolute inset-0 rounded-full border-4 border-t-orange-500 border-r-transparent border-b-transparent border-l-transparent animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-orange-500 animate-spin" />
          </div>
        </div>

        {/* Status Text */}
        <div>
          <h2 className="text-xl font-semibold text-white mb-2">
            Creating Your Edit
          </h2>
          <p className="text-neutral-400">
            This usually takes 1–3 minutes depending on video length.
          </p>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-neutral-800 rounded-full h-2 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-orange-600 to-red-500 rounded-full transition-all duration-700 ease-out"
            style={{ width: `${Math.max(5, 0)}%` }}
          />
        </div>

        {/* Steps */}
        <div className="space-y-3 text-left">
          {[
            { key: "uploading", label: "Upload received" },
            { key: "analyzing", label: "Finding best moments" },
            { key: "editing", label: "Stitching clips together" },
            { key: "rendering", label: "Rendering final video" },
          ].map((step) => (
            <div key={step.key} className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
              </div>
              <span className="text-sm text-neutral-300">{step.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
