'use client';

import { useState, useRef, useEffect, useCallback } from 'react';

interface AudioRecorderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSendAudio: (file: File) => void;
  disabled?: boolean;
}

interface AudioDevice {
  deviceId: string;
  label: string;
}

function writeString(view: DataView, offset: number, string: string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}

function encodeWAV(samples: Float32Array, sampleRate: number): Blob {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM format
  view.setUint16(22, 1, true); // Mono
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, 'data');
  view.setUint32(40, samples.length * 2, true);

  let offset = 44;
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }

  return new Blob([view], { type: 'audio/wav' });
}

export default function AudioRecorderModal({ isOpen, onClose, onSendAudio, disabled }: AudioRecorderModalProps) {
  const [recording, setRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [micError, setMicError] = useState<string | null>(null);
  const [isMinimized, setIsMinimized] = useState(false);

  // Microphone Device & Audio Settings
  const [devices, setDevices] = useState<AudioDevice[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>('');
  const [showSettings, setShowSettings] = useState(false);
  const [noiseSuppression, setNoiseSuppression] = useState(true);
  const [echoCancellation, setEchoCancellation] = useState(true);
  const [autoGainControl, setAutoGainControl] = useState(true);
  const [audioLevel, setAudioLevel] = useState(0);

  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const chunksRef = useRef<Float32Array[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Enumerate audio input devices
  const loadAudioDevices = useCallback(async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
      const allDevices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = allDevices
        .filter((device) => device.kind === 'audioinput')
        .map((d, index) => ({
          deviceId: d.deviceId,
          label: d.label || `Mikrofon ${index + 1} (${d.deviceId.slice(0, 5)}...)`,
        }));
      setDevices(audioInputs);
      if (audioInputs.length > 0 && !selectedDeviceId) {
        setSelectedDeviceId(audioInputs[0].deviceId);
      }
    } catch (e) {
      console.warn('Could not enumerate audio devices:', e);
    }
  }, [selectedDeviceId]);

  useEffect(() => {
    if (isOpen) {
      loadAudioDevices();
    } else {
      cleanup();
    }
  }, [isOpen, loadAudioDevices]);

  const cleanup = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }
    if (analyserRef.current) {
      analyserRef.current.disconnect();
      analyserRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    setRecording(false);
    setRecordingTime(0);
    setAudioLevel(0);
    setIsMinimized(false);
  };

  const startRecording = async () => {
    setMicError(null);
    setAudioBlob(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
    chunksRef.current = [];

    try {
      const constraints: MediaStreamConstraints = {
        audio: {
          deviceId: selectedDeviceId ? { exact: selectedDeviceId } : undefined,
          noiseSuppression,
          echoCancellation,
          autoGainControl,
          channelCount: 1,
          sampleRate: 16000,
        },
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      // Refresh devices in case labels were previously restricted by browser permissions
      loadAudioDevices();

      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      const audioCtx = new AudioCtx({ sampleRate: 16000 });
      audioContextRef.current = audioCtx;

      const source = audioCtx.createMediaStreamSource(stream);
      sourceRef.current = source;

      // Analyser Node for Live VU Meter
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;
      source.connect(analyser);

      // ScriptProcessor for WAV Recording (4096 buffer size, mono)
      const processor = audioCtx.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        chunksRef.current.push(new Float32Array(inputData));
      };

      source.connect(processor);
      processor.connect(audioCtx.destination);

      // Update Audio Level Visualizer loop
      const updateLevel = () => {
        if (!analyserRef.current) return;
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);
        const avg = dataArray.reduce((p, c) => p + c, 0) / dataArray.length;
        setAudioLevel(Math.min(100, Math.round((avg / 128) * 100)));
        animationFrameRef.current = requestAnimationFrame(updateLevel);
      };
      updateLevel();

      setRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      console.error('Microphone error:', err);
      setMicError(
        err.name === 'NotAllowedError'
          ? 'Izin mikrofon ditolak. Berikan izin di browser Anda.'
          : `Gagal mengakses mikrofon: ${err.message || 'Perangkat tidak tersedia'}`,
      );
    }
  };

  const stopRecording = () => {
    if (!recording) return;

    if (timerRef.current) clearInterval(timerRef.current);
    if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    setRecording(false);
    setAudioLevel(0);

    // Merge recorded chunks
    const totalLength = chunksRef.current.reduce((acc, chunk) => acc + chunk.length, 0);
    const mergedSamples = new Float32Array(totalLength);
    let offset = 0;
    for (const chunk of chunksRef.current) {
      mergedSamples.set(chunk, offset);
      offset += chunk.length;
    }

    const sampleRate = audioContextRef.current?.sampleRate || 16000;
    const wavBlob = encodeWAV(mergedSamples, sampleRate);
    setAudioBlob(wavBlob);
    setAudioUrl(URL.createObjectURL(wavBlob));

    // Cleanup recording resources
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }
    if (analyserRef.current) {
      analyserRef.current.disconnect();
      analyserRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const stopAndSendDirectly = () => {
    if (recording) {
      if (timerRef.current) clearInterval(timerRef.current);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      setRecording(false);

      const totalLength = chunksRef.current.reduce((acc, chunk) => acc + chunk.length, 0);
      const mergedSamples = new Float32Array(totalLength);
      let offset = 0;
      for (const chunk of chunksRef.current) {
        mergedSamples.set(chunk, offset);
        offset += chunk.length;
      }

      const sampleRate = audioContextRef.current?.sampleRate || 16000;
      const wavBlob = encodeWAV(mergedSamples, sampleRate);

      if (processorRef.current) {
        processorRef.current.disconnect();
        processorRef.current = null;
      }
      if (sourceRef.current) {
        sourceRef.current.disconnect();
        sourceRef.current = null;
      }
      if (analyserRef.current) {
        analyserRef.current.disconnect();
        analyserRef.current = null;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }

      const filename = `recording_${Date.now()}.wav`;
      const file = new File([wavBlob], filename, { type: 'audio/wav' });
      onSendAudio(file);
      handleClose();
    } else if (audioBlob) {
      handleSend();
    }
  };

  const handleSend = () => {
    if (!audioBlob) return;
    const filename = `recording_${Date.now()}.wav`;
    const file = new File([audioBlob], filename, { type: 'audio/wav' });
    onSendAudio(file);
    handleClose();
  };

  const handleClose = () => {
    cleanup();
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioBlob(null);
    setAudioUrl(null);
    setMicError(null);
    setIsMinimized(false);
    onClose();
  };

  const formatSeconds = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  if (!isOpen) return null;

  // MINIMIZED FLOATING DOCK: Doctor can keep recording in background and chat freely!
  if (isMinimized && (recording || audioBlob)) {
    return (
      <div className="fixed top-16 sm:top-20 right-4 sm:right-6 z-50 bg-emerald-950/95 dark:bg-slate-900/95 text-white backdrop-blur-md px-4 py-2.5 rounded-2xl shadow-2xl border border-emerald-400/40 flex items-center gap-3 animate-in slide-in-from-top-2 duration-150">
        <div className="flex items-center gap-2">
          {recording ? (
            <>
              <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
              <span className="text-[10px] font-bold tracking-wider text-red-400 uppercase bg-red-950/80 px-1.5 py-0.5 rounded border border-red-800/60">
                REC
              </span>
            </>
          ) : (
            <span className="text-xs">⏸️</span>
          )}
          <span className="font-mono text-xs font-bold text-emerald-200">
            {formatSeconds(recordingTime)}
          </span>
          {recording && (
            <div className="w-12 h-2 bg-emerald-900 rounded-full overflow-hidden border border-emerald-700/60 ml-1">
              <div
                className="h-full bg-gradient-to-r from-emerald-400 to-amber-400 transition-all duration-75"
                style={{ width: `${Math.max(10, audioLevel)}%` }}
              />
            </div>
          )}
        </div>

        <div className="h-4 w-px bg-emerald-700/60" />

        <span className="text-[11px] text-emerald-300 hidden md:inline font-medium">
          Merekam aktif — Silakan lanjutkan chat & konsultasi dengan bot
        </span>

        <div className="flex items-center gap-1.5 ml-auto">
          <button
            type="button"
            onClick={stopAndSendDirectly}
            disabled={disabled}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-xs flex items-center gap-1.5 transition-all"
          >
            <span>⏹️</span>
            <span>Selesai & Kirim</span>
          </button>

          <button
            type="button"
            onClick={() => setIsMinimized(false)}
            title="Buka panel rekam penuh"
            className="p-1.5 rounded-lg bg-emerald-900/80 hover:bg-emerald-800 text-emerald-200 hover:text-white text-xs font-semibold"
          >
            🔍 Perluas
          </button>

          <button
            type="button"
            onClick={handleClose}
            title="Batalkan rekaman"
            className="p-1.5 rounded-lg hover:bg-red-900/60 text-slate-400 hover:text-red-300 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-lg bg-white dark:bg-slate-900 rounded-3xl border border-emerald-300 dark:border-slate-700 shadow-2xl p-6 relative">
        <div className="absolute top-4 right-4 flex items-center gap-1.5">
          {recording && (
            <button
              type="button"
              onClick={() => setIsMinimized(true)}
              title="Minimalkan agar bisa lanjut chat sambil merekam"
              className="px-2.5 py-1 rounded-xl bg-emerald-100 dark:bg-slate-800 hover:bg-emerald-200 text-emerald-800 dark:text-emerald-300 text-xs font-bold flex items-center gap-1 shadow-2xs"
            >
              <span>🔽</span>
              <span>Minimalkan (Lanjut Chat)</span>
            </button>
          )}
          <button
            type="button"
            onClick={handleClose}
            className="p-1 text-emerald-700 dark:text-slate-400 hover:text-emerald-950 dark:hover:text-white text-sm font-bold w-7 h-7 rounded-full bg-emerald-50 dark:bg-slate-800 flex items-center justify-center"
          >
            ✕
          </button>
        </div>

        <div className="text-center mb-4 mt-1">
          <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-slate-800 text-emerald-700 dark:text-emerald-300 flex items-center justify-center text-2xl mx-auto mb-2 shadow-2xs">
            🎙️
          </div>
          <h3 className="text-base font-bold text-emerald-950 dark:text-white">Rekam Konsultasi Klinis (WAV)</h3>
          <p className="text-xs text-emerald-700 dark:text-slate-400 mt-0.5">
            Gemini STT akan mentranskripsikan suara &amp; membuat resume otomatis S/O/A.
          </p>
        </div>

        {micError && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 text-xs text-center">
            {micError}
          </div>
        )}

        {/* Recording Animation, VU Meter & Timer */}
        <div className="flex flex-col items-center justify-center py-5 bg-emerald-50/70 dark:bg-slate-800/60 border border-emerald-200/80 dark:border-slate-700 rounded-2xl mb-4">
          <div className="text-3xl font-mono font-bold text-emerald-950 dark:text-white mb-2">
            {formatSeconds(recordingTime)}
          </div>

          {recording ? (
            <div className="flex flex-col items-center gap-2 w-full px-8">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-500 animate-ping" />
                <span className="text-xs font-semibold text-red-600 dark:text-red-400">Sedang merekam suara...</span>
              </div>

              {/* Real-time VU Audio Level Meter */}
              <div className="w-full h-3 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden p-0.5 border border-emerald-300 dark:border-slate-600">
                <div
                  className={`h-full rounded-full transition-all duration-75 ${
                    audioLevel > 75
                      ? 'bg-gradient-to-r from-emerald-500 via-amber-500 to-red-500'
                      : 'bg-gradient-to-r from-emerald-400 to-emerald-600'
                  }`}
                  style={{ width: `${Math.max(5, audioLevel)}%` }}
                />
              </div>

              <button
                type="button"
                onClick={() => setIsMinimized(true)}
                className="mt-1 px-3 py-1 bg-white dark:bg-slate-900 border border-emerald-300 dark:border-slate-700 rounded-xl text-[11px] font-bold text-emerald-800 dark:text-emerald-300 hover:bg-emerald-50 shadow-2xs"
              >
                💬 Minimalkan untuk chat dengan bot saat merekam
              </button>
            </div>
          ) : audioBlob ? (
            <div className="text-xs text-emerald-700 dark:text-emerald-300 font-medium mb-1">
              Rekaman selesai ({Math.round(audioBlob.size / 1024)} KB)
            </div>
          ) : (
            <div className="text-xs text-emerald-600 dark:text-slate-400">Siap merekam konsultasi klinis</div>
          )}

          {/* Audio Player Preview */}
          {audioUrl && !recording && (
            <audio controls src={audioUrl} className="mt-3 w-4/5 h-8" />
          )}
        </div>

        {/* Microphone Device & Audio Setting Panel */}
        <div className="mb-4 rounded-2xl border border-emerald-200 dark:border-slate-700 bg-white/80 dark:bg-slate-800/80 p-3 space-y-2.5">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-emerald-950 dark:text-slate-200 flex items-center gap-1.5">
              <span>🎙️</span>
              <span>Pilihan Mikrofon:</span>
            </label>
            <button
              type="button"
              onClick={() => setShowSettings(!showSettings)}
              className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 hover:underline flex items-center gap-1"
            >
              <span>⚙️ {showSettings ? 'Sembunyikan Pengaturan' : 'Filter Audio'}</span>
            </button>
          </div>

          {/* Device Selection Dropdown */}
          <div className="relative">
            <select
              value={selectedDeviceId}
              onChange={(e) => setSelectedDeviceId(e.target.value)}
              disabled={recording}
              className="w-full pl-3 pr-8 py-2 rounded-xl border border-emerald-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-medium text-emerald-950 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {devices.length === 0 ? (
                <option value="">Mikrofon Bawaan Sistem (Default)</option>
              ) : (
                devices.map((d) => (
                  <option key={d.deviceId} value={d.deviceId}>
                    {d.label}
                  </option>
                ))
              )}
            </select>
          </div>

          {/* Advanced Audio Filters Options */}
          {showSettings && (
            <div className="pt-2 border-t border-emerald-100 dark:border-slate-700/80 grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px]">
              <label className="flex items-center gap-1.5 cursor-pointer text-emerald-900 dark:text-slate-300">
                <input
                  type="checkbox"
                  checked={noiseSuppression}
                  onChange={(e) => setNoiseSuppression(e.target.checked)}
                  disabled={recording}
                  className="rounded text-emerald-600 focus:ring-emerald-500"
                />
                <span>Peredam Bising</span>
              </label>

              <label className="flex items-center gap-1.5 cursor-pointer text-emerald-900 dark:text-slate-300">
                <input
                  type="checkbox"
                  checked={echoCancellation}
                  onChange={(e) => setEchoCancellation(e.target.checked)}
                  disabled={recording}
                  className="rounded text-emerald-600 focus:ring-emerald-500"
                />
                <span>Anti Gema</span>
              </label>

              <label className="flex items-center gap-1.5 cursor-pointer text-emerald-900 dark:text-slate-300">
                <input
                  type="checkbox"
                  checked={autoGainControl}
                  onChange={(e) => setAutoGainControl(e.target.checked)}
                  disabled={recording}
                  className="rounded text-emerald-600 focus:ring-emerald-500"
                />
                <span>Auto Gain Volume</span>
              </label>
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div className="flex gap-2.5">
          {!recording && !audioBlob && (
            <button
              type="button"
              onClick={startRecording}
              disabled={disabled}
              className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold rounded-xl text-xs transition-all shadow-md flex items-center justify-center gap-2"
            >
              <span>🔴</span>
              <span>Mulai Merekam</span>
            </button>
          )}

          {recording && (
            <>
              <button
                type="button"
                onClick={() => setIsMinimized(true)}
                className="flex-1 py-3 bg-emerald-100 dark:bg-slate-800 hover:bg-emerald-200 text-emerald-900 dark:text-emerald-300 font-bold rounded-xl text-xs border border-emerald-300 dark:border-slate-700 transition-all flex items-center justify-center gap-1.5"
              >
                <span>💬</span>
                <span>Lanjut Chat</span>
              </button>
              <button
                type="button"
                onClick={stopRecording}
                className="flex-1 py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl text-xs transition-all shadow-md flex items-center justify-center gap-1.5 animate-pulse"
              >
                <span>⏹️</span>
                <span>Hentikan Rekaman</span>
              </button>
            </>
          )}

          {audioBlob && !recording && (
            <>
              <button
                type="button"
                onClick={startRecording}
                className="flex-1 py-2.5 bg-emerald-100 dark:bg-slate-800 hover:bg-emerald-200 text-emerald-900 dark:text-emerald-300 font-semibold rounded-xl text-xs border border-emerald-300 dark:border-slate-700 transition-colors"
              >
                🔄 Rekam Ulang
              </button>
              <button
                type="button"
                onClick={handleSend}
                disabled={disabled}
                className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold rounded-xl text-xs transition-all shadow-md"
              >
                🚀 Kirim &amp; Evaluasi S/O/A
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
