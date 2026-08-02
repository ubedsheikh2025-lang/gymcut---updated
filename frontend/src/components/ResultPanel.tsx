"use client";

import { useState } from "react";
import { Download, RotateCcw, Play, CheckCircle2, Clock, Scissors } from "lucide-react";
import { getDownloadUrl } from "@/lib/api";
import { formatDuration } from "@/lib/utils";
import type { JobStatus } from "@/lib/api";

interface ResultPanelProps {
  jobStatus: JobStatus;
  jobId: string;
  onReset: () => void;
}

export function ResultPanel({ jobStatus, jobId, onReset }: ResultPanelProps) {
  const [showVideo, setShowVideo] = useState(false);
  const downloadUrl = getDownloadUrl(jobId);

  const totalDuration = jobStatus.highlights.reduce(
    (sum, h) => sum + (h.end - h.start),
    0
  );

  return (
    <div className="w-full max-w-2xl animate-in space-y-6">
      {/* Success Card */}
      <div className="glass-card p-8 text-center space-y-6">
        <div className="w-20 h-20 mx-auto rounded-full bg-green-500/10 flex items-center justify-center">
          <CheckCircle2 className="w-10 h-10 text-green-500" />
        </div>

        <div>
          <h2 className="text-2xl font-bold text-white mb-2">
            Your Video is Ready!
          </h2>
          <p className="text-neutral-400">
            AI found {jobStatus.highlights.length} highlight{" "}
            {jobStatus.highlights.length !== 1 ? "moments" : "moment"} and
            stitched them together.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-neutral-800 rounded-xl p-4">
            <Scissors className="w-5 h-5 text-orange-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-white">
              {jobStatus.highlights.length}
            </p>
            <p className="text-xs text-neutral-500">Clips</p>
          </div>
          <div className="bg-neutral-800 rounded-xl p-4">
            <Clock className="w-5 h-5 text-orange-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-white">
              {formatDuration(totalDuration)}
            </p>
            <p className="text-xs text-neutral-500">Duration</p>
          </div>
          <div className="bg-neutral-800 rounded-xl p-4">
            <Play className="w-5 h-5 text-orange-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-white">HD</p>
            <p className="text-xs text-neutral-500">Quality</p>
          </div>
        </div>

        {/* Video Preview */}
        {showVideo && (
          <div className="rounded-xl overflow-hidden bg-black">
            <video
              controls
              className="w-full"
              src={downloadUrl}
              style={{ maxHeight: "400px" }}
            >
              Your browser does not support the video tag.
            </video>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3">
          <a
            href={downloadUrl}
            download
            className="btn-primary flex-1 flex items-center justify-center gap-2"
          >
            <Download className="w-5 h-5" />
            Download Video
          </a>
          <button
            onClick={() => setShowVideo(!showVideo)}
            className="btn-secondary flex items-center justify-center gap-2"
          >
            <Play className="w-5 h-5" />
            {showVideo ? "Hide Preview" : "Preview"}
          </button>
        </div>
      </div>

      {/* Highlights List */}
      {jobStatus.highlights.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-white font-semibold mb-4">
            Detected Highlights
          </h3>
          <div className="space-y-2">
            {jobStatus.highlights.map((h, i) => (
              <div
                key={i}
                className="flex items-center justify-between py-2 px-3 rounded-lg bg-neutral-800/50"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs text-neutral-600 font-mono w-6">
                    #{i + 1}
                  </span>
                  {h.label && (
                    <span className="text-xs bg-neutral-700 px-2 py-0.5 rounded-full text-neutral-300">
                      {h.label}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-neutral-400">
                    {formatDuration(h.start)} – {formatDuration(h.end)}
                  </span>
                  <span className="text-orange-500 font-mono text-xs">
                    {Math.round(h.score * 100)}% match
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reset */}
      <div className="text-center">
        <button
          onClick={onReset}
          className="text-neutral-500 hover:text-white transition-colors text-sm flex items-center gap-2 mx-auto"
        >
          <RotateCcw className="w-4 h-4" />
          Edit Another Video
        </button>
      </div>
    </div>
  );
}
