import React, { useEffect, useRef, useState } from "react";
import { Play, Pause, RotateCcw, RotateCw, Volume2, VolumeX, Music, Video, BookmarkCheck } from "lucide-react";
import {
  mediaPlayerEngine,
  getSavedMediaTimestamp,
  saveLocalMediaBookmark,
} from "@/lib/media";
import { cn } from "@/lib/utils";

interface MediaPlayerProps {
  id: string;
  url: string;
  title: string;
  type?: "audio" | "video";
  className?: string;
  autoPlay?: boolean;
}

function formatTime(seconds: number): string {
  if (isNaN(seconds) || seconds < 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  const hrs = Math.floor(mins / 60);
  if (hrs > 0) {
    const remMins = mins % 60;
    return `${hrs}:${remMins < 10 ? "0" : ""}${remMins}:${secs < 10 ? "0" : ""}${secs}`;
  }
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

export function MediaPlayer({
  id,
  url,
  title,
  type = "audio",
  className,
  autoPlay = false,
}: MediaPlayerProps) {
  const mediaRef = useRef<HTMLMediaElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [muted, setMuted] = useState(false);
  const [hasResumed, setHasResumed] = useState(false);
  const initialSavedTime = useRef(getSavedMediaTimestamp(id));

  useEffect(() => {
    const el = mediaRef.current;
    if (!el) return;

    mediaPlayerEngine.attachElement({ id, title, url, type }, el);

    const onLoadedMetadata = () => {
      setDuration(el.duration);
      const saved = getSavedMediaTimestamp(id);
      if (saved > 0 && saved < el.duration) {
        el.currentTime = saved;
        setCurrentTime(saved);
        setHasResumed(true);
      }
    };

    const onTimeUpdate = () => {
      setCurrentTime(el.currentTime);
      mediaPlayerEngine.updateProgress(el.currentTime, el.duration, !el.paused);
    };

    const onPlay = () => setIsPlaying(true);
    const onPause = () => {
      setIsPlaying(false);
      saveLocalMediaBookmark(id, el.currentTime, el.duration);
    };
    const onEnded = () => {
      setIsPlaying(false);
      saveLocalMediaBookmark(id, 0, el.duration);
      setCurrentTime(0);
    };

    el.addEventListener("loadedmetadata", onLoadedMetadata);
    el.addEventListener("timeupdate", onTimeUpdate);
    el.addEventListener("play", onPlay);
    el.addEventListener("pause", onPause);
    el.addEventListener("ended", onEnded);

    if (autoPlay) {
      el.play().catch(() => {});
    }

    return () => {
      el.removeEventListener("loadedmetadata", onLoadedMetadata);
      el.removeEventListener("timeupdate", onTimeUpdate);
      el.removeEventListener("play", onPlay);
      el.removeEventListener("pause", onPause);
      el.removeEventListener("ended", onEnded);
      saveLocalMediaBookmark(id, el.currentTime, el.duration);
    };
  }, [id, title, url, type, autoPlay]);

  const togglePlay = () => {
    const el = mediaRef.current;
    if (!el) return;
    if (el.paused) {
      el.play().catch(() => {});
    } else {
      el.pause();
    }
  };

  const skip = (seconds: number) => {
    const el = mediaRef.current;
    if (!el) return;
    const target = Math.max(0, Math.min(el.duration || 999999, el.currentTime + seconds));
    el.currentTime = target;
    setCurrentTime(target);
    saveLocalMediaBookmark(id, target, el.duration);
  };

  const onSeekChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const el = mediaRef.current;
    if (!el) return;
    const val = parseFloat(e.target.value);
    el.currentTime = val;
    setCurrentTime(val);
    saveLocalMediaBookmark(id, val, el.duration);
  };

  const toggleMute = () => {
    const el = mediaRef.current;
    if (!el) return;
    el.muted = !el.muted;
    setMuted(el.muted);
  };

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div
      className={cn(
        "glass rounded-3xl p-4 border border-border/80 shadow-xs transition-all space-y-3",
        className
      )}
    >
      {/* Video Viewport if applicable */}
      {type === "video" ? (
        <div className="relative aspect-video w-full overflow-hidden rounded-2xl bg-black/80 flex items-center justify-center">
          <video
            ref={mediaRef as React.RefObject<HTMLVideoElement>}
            src={url}
            className="h-full w-full object-contain"
            playsInline
            onClick={togglePlay}
          />
        </div>
      ) : (
        <audio ref={mediaRef as React.RefObject<HTMLAudioElement>} src={url} preload="metadata" />
      )}

      {/* Header Info */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-primary/10 text-primary">
            {type === "video" ? <Video className="size-4" /> : <Music className="size-4" />}
          </span>
          <div className="min-w-0">
            <h4 className="text-sm font-semibold truncate text-foreground">{title}</h4>
            <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
              <span>{type.toUpperCase()}</span>
              {hasResumed && initialSavedTime.current > 0 ? (
                <span className="inline-flex items-center gap-0.5 text-primary font-medium">
                  • <BookmarkCheck className="size-3" /> Resumed from {formatTime(initialSavedTime.current)}
                </span>
              ) : null}
            </div>
          </div>
        </div>

        {/* Volume button */}
        <button
          type="button"
          onClick={toggleMute}
          className="p-1.5 text-muted-foreground hover:text-foreground transition-colors rounded-lg hover:bg-accent"
          aria-label={muted ? "Unmute" : "Mute"}
        >
          {muted ? <VolumeX className="size-4 text-destructive" /> : <Volume2 className="size-4" />}
        </button>
      </div>

      {/* Progress & Scrubbing Bar */}
      <div className="space-y-1">
        <div className="relative flex items-center">
          <input
            type="range"
            min={0}
            max={duration || 100}
            step={0.1}
            value={currentTime}
            onChange={onSeekChange}
            aria-label="Seek media position"
            className="w-full h-1.5 appearance-none rounded-lg bg-muted accent-primary cursor-pointer"
            style={{
              background: `linear-gradient(to right, var(--color-primary, #3b82f6) ${progressPercent}%, var(--color-muted, #334155) ${progressPercent}%)`,
            }}
          />
        </div>
        <div className="flex items-center justify-between text-[11px] text-muted-foreground tabular-nums px-0.5">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Playback Controls */}
      <div className="flex items-center justify-center gap-3 pt-1">
        <button
          type="button"
          onClick={() => skip(-10)}
          aria-label="Rewind 10 seconds"
          className="grid size-9 place-items-center rounded-full text-muted-foreground hover:bg-accent hover:text-foreground transition-all active:scale-95"
        >
          <RotateCcw className="size-4" />
        </button>

        <button
          type="button"
          onClick={togglePlay}
          aria-label={isPlaying ? "Pause playback" : "Resume playback"}
          className="grid size-11 place-items-center rounded-full bg-primary text-primary-foreground shadow-md transition-transform active:scale-95 hover:opacity-95"
        >
          {isPlaying ? <Pause className="size-5" /> : <Play className="size-5 ml-0.5" />}
        </button>

        <button
          type="button"
          onClick={() => skip(10)}
          aria-label="Skip forward 10 seconds"
          className="grid size-9 place-items-center rounded-full text-muted-foreground hover:bg-accent hover:text-foreground transition-all active:scale-95"
        >
          <RotateCw className="size-4" />
        </button>
      </div>
    </div>
  );
}
