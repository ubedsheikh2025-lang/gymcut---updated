// API client for the Gym Video AI Editor backend.

const API_BASE = "";

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

  // Get the raw text first for debugging
  const rawText = await response.text();
  
  if (!response.ok) {
    // Try to parse as JSON, fall back to raw text
    try {
      const error = JSON.parse(rawText);
      throw new Error(error.detail || "Upload failed");
    } catch (e) {
      if (e instanceof SyntaxError) {
        throw new Error(`Upload failed (${response.status}): ${rawText.slice(0, 200)}`);
      }
      throw e;
    }
  }

  // Parse the success response
  try {
    return JSON.parse(rawText);
  } catch (e) {
    throw new Error(`Invalid JSON response: ${rawText.slice(0, 200)}`);
  }
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await fetch(`${API_BASE}/api/jobs/${jobId}`);

  if (!response.ok) {
    throw new Error("Failed to fetch job status");
  }

  const rawText = await response.text();
  return JSON.parse(rawText);
}

export function getDownloadUrl(jobId: string): string {
  return `${API_BASE}/api/jobs/${jobId}/download`;
}

export async function checkHealth(): Promise<{ status: string; ffmpeg: boolean }> {
  const response = await fetch(`${API_BASE}/api/health`);
  const rawText = await response.text();
  return JSON.parse(rawText);
}
