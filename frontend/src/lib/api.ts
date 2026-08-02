// API client for the Gym Video AI Editor backend.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface JobStatus {
  job_id: string;
  status: "uploading" | "analyzing" | "editing" | "rendering" | "done" | "failed";
  progress: number;
  message: string;
  output_url: string | null;
  highlights: Highlight[];
}

export interface Highlight {
  start: number;
  end: number;
  score: number;
  label?: string;
}

export interface UploadResponse {
  job_id: string;
  status: string;
}

export async function uploadVideo(
  file: File,
  options: {
    useAI?: boolean;
    musicStyle?: string;
    durationTarget?: number;
  } = {}
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("use_ai", String(options.useAI ?? false));
  formData.append("music_style", options.musicStyle ?? "energetic");
  formData.append("duration_target", String(options.durationTarget ?? 60));

  const response = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Upload failed");
  }

  return response.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await fetch(`${API_BASE}/api/jobs/${jobId}`);

  if (!response.ok) {
    throw new Error("Failed to fetch job status");
  }

  return response.json();
}

export function getDownloadUrl(jobId: string): string {
  return `${API_BASE}/api/jobs/${jobId}/download`;
}

export async function checkHealth(): Promise<{ status: string; ffmpeg: boolean }> {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}

