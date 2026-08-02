"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, Film, X, Sparkles, Zap } from "lucide-react";
import { uploadVideo } from "@/lib/api";
import { formatFileSize } from "@/lib/utils";

interface UploadZoneProps {
  onUploadStart: () => void;
  onProcessingStart: (jobId: string) => void;
  onError: (message: string) => void;
  disabled: boolean;
}

export function UploadZone({
  onUploadStart,
  onProcessingStart,
  onError,
  disabled,
}: UploadZoneProps) {
  const [file, setFile] = useState<File | null>(null);
  const [useAI, setUseAI] = useState(false);
  const [durationTarget, setDurationTarget] = useState(60);
  const [musicStyle, setMusicStyle] = useState("energetic");

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/*": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    },
    maxFiles: 1,
    maxSize: 500 * 1024 * 1024, // 500MB
    disabled,
  });

  const handleUpload = async () => {
    if (!file) return;

    try {
      onUploadStart();
      const response = await uploadVideo(file, {
        useAI,
        musicStyle,
        durationTarget,
      });
      onProcessingStart(response.job_id);
    } catch (err: any) {
      onError(err.message || "Upload failed. Please try again.");
    }
  };

  const clearFile = () => setFile(null);

  return (
    <div className="w-full max-w-2xl animate-in">
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`
          glass-card p-10 md:p-16 text-center cursor-pointer transition-all duration-300
          ${isDragActive ? "border-orange-500 bg-orange-500/5 scale-[1.02]" : "hover:border-neutral-600"}
          ${disabled ? "opacity-50 pointer-events-none" : ""}
        `}
      >
        <input {...getInputProps()} />

        {file ? (
          /* File Selected */
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-neutral-800 flex items-center justify-center">
              <Film className="w-8 h-8 text-orange-500" />
            </div>
            <div>
              <p className="text-white font-semibold text-lg truncate max-w-xs mx-auto">
                {file.name}
              </p>
              <p className="text-neutral-500 text-sm">{formatFileSize(file.size)}</p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                clearFile();
              }}
              className="text-neutral-500 hover:text-white transition-colors text-sm flex items-center gap-1 mx-auto"
            >
              <X className="w-4 h-4" />
              Remove
            </button>
          </div>
        ) : isDragActive ? (
          /* Dragging */
          <div className="space-y-4">
            <div className="w-20 h-20 mx-auto rounded-full bg-orange-500/10 flex items-center justify-center animate-pulse">
              <Upload className="w-10 h-10 text-orange-500" />
            </div>
            <p className="text-orange-500 font-semibold text-xl">Drop your video here</p>
          </div>
        ) : (
          /* Default */
          <div className="space-y-4">
            <div className="w-20 h-20 mx-auto rounded-full bg-neutral-800 flex items-center justify-center">
              <Upload className="w-10 h-10 text-neutral-400" />
            </div>
            <div>
              <p className="text-white font-semibold text-xl">
                Drop your gym video here
              </p>
              <p className="text-neutral-500 mt-1">
                or click to browse — MP4, MOV, AVI (max 500MB)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Options */}
      {file && (
        <div className="glass-card p-6 mt-4 space-y-5 animate-in">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-orange-500" />
            Edit Options
          </h3>

          {/* AI Toggle */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white text-sm font-medium">AI Detection</p>
              <p className="text-neutral-500 text-xs">
                Use AI to find the best workout moments (requires Google Cloud)
              </p>
            </div>
            <button
              onClick={() => setUseAI(!useAI)}
              className={`
                relative w-12 h-6 rounded-full transition-colors duration-200
                ${useAI ? "bg-orange-600" : "bg-neutral-700"}
              `}
            >
              <div
                className={`
                  absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform duration-200
                  ${useAI ? "translate-x-6" : "translate-x-0.5"}
                `}
              />
            </button>
          </div>

          {/* Duration */}
          <div>
            <label className="text-white text-sm font-medium block mb-2">
              Target Duration: {durationTarget}s
            </label>
            <input
              type="range"
              min={15}
              max={180}
              step={5}
              value={durationTarget}
              onChange={(e) => setDurationTarget(Number(e.target.value))}
              className="w-full accent-orange-500"
            />
            <div className="flex justify-between text-xs text-neutral-600 mt-1">
              <span>15s</span>
              <span>180s</span>
            </div>
          </div>

          {/* Music Style */}
          <div>
            <label className="text-white text-sm font-medium block mb-2">
              Music Style
            </label>
            <div className="grid grid-cols-3 gap-2">
              {["energetic", "motivational", "chill"].map((style) => (
                <button
                  key={style}
                  onClick={() => setMusicStyle(style)}
                  className={`
                    py-2 px-3 rounded-lg text-sm font-medium capitalize transition-all
                    ${
                      musicStyle === style
                        ? "bg-orange-600 text-white"
                        : "bg-neutral-800 text-neutral-400 hover:bg-neutral-700"
                    }
                  `}
                >
                  {style}
                </button>
              ))}
            </div>
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={disabled}
            className="btn-primary w-full flex items-center justify-center gap-2 text-lg"
          >
            <Zap className="w-5 h-5" />
            {disabled ? "Uploading..." : "Start Auto-Edit"}
          </button>
        </div>
      )}
    </div>
  );
}
