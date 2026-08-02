"use client";

import { useState, useCallback } from "react";
import { Header } from "@/components/Header";
import { UploadZone } from "@/components/UploadZone";
import { ProcessingPanel } from "@/components/ProcessingPanel";
import { ResultPanel } from "@/components/ResultPanel";
import { Features } from "@/components/Features";
import { Footer } from "@/components/Footer";
import type { JobStatus } from "@/lib/api";

type AppState = "idle" | "uploading" | "processing" | "done" | "failed";

export default function Home() {
  const [appState, setAppState] = useState<AppState>("idle");
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUploadStart = useCallback(() => {
    setAppState("uploading");
    setError(null);
  }, []);

  const handleProcessingStart = useCallback((id: string) => {
    setJobId(id);
    setAppState("processing");
  }, []);

  const handleStatusUpdate = useCallback((status: JobStatus) => {
    setJobStatus(status);
    if (status.status === "done") {
      setAppState("done");
    } else if (status.status === "failed") {
      setAppState("failed");
      setError(status.message);
    }
  }, []);

  const handleReset = useCallback(() => {
    setAppState("idle");
    setJobId(null);
    setJobStatus(null);
    setError(null);
  }, []);

  const handleError = useCallback((msg: string) => {
    setAppState("failed");
    setError(msg);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 flex flex-col items-center px-4 py-8 md:py-16">
        {/* Hero — only shown when idle */}
        {appState === "idle" && (
          <div className="text-center mb-12 animate-in">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4">
              Your Gym Videos,
              <br />
              <span className="gradient-text">Edited by AI</span>
            </h1>
            <p className="text-neutral-400 text-lg md:text-xl max-w-2xl mx-auto">
              Upload raw workout footage. AI finds your best lifts, poses, and
              action moments — then stitches them into a polished reel. Zero
              editing skills needed.
            </p>
          </div>
        )}

        {/* Upload Zone */}
        {(appState === "idle" || appState === "uploading") && (
          <UploadZone
            onUploadStart={handleUploadStart}
            onProcessingStart={handleProcessingStart}
            onError={handleError}
            disabled={appState === "uploading"}
          />
        )}

        {/* Processing */}
        {appState === "processing" && jobId && (
          <ProcessingPanel
            jobId={jobId}
            onStatusUpdate={handleStatusUpdate}
            onError={handleError}
          />
        )}

        {/* Result */}
        {appState === "done" && jobStatus && jobId && (
          <ResultPanel
            jobStatus={jobStatus}
            jobId={jobId}
            onReset={handleReset}
          />
        )}

        {/* Error */}
        {appState === "failed" && (
          <div className="glass-card p-8 max-w-lg w-full text-center animate-in">
            <div className="text-red-500 text-5xl mb-4">⚠</div>
            <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
            <p className="text-neutral-400 mb-6">{error || "An unknown error occurred."}</p>
            <button onClick={handleReset} className="btn-primary">
              Try Again
            </button>
          </div>
        )}

        {/* Features — only shown when idle */}
        {appState === "idle" && <Features />}
      </main>

      <Footer />
    </div>
  );
}
