'use client';

import { useEffect, useState } from 'react';

export default function ConnectionStatusBanner() {
  const [isDisconnected, setIsDisconnected] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isReconnecting, setIsReconnecting] = useState(false);

  useEffect(() => {
    const handleConnectionError = (event: Event) => {
      const customEvent = event as CustomEvent<{ message?: string; status?: number }>;
      setIsDisconnected(true);
      setErrorMessage(
        customEvent.detail?.message ||
          'Tidak dapat terhubung ke server medis backend. Server mungkin sedang dimulai ulang.'
      );
    };

    const handleConnectionRestored = () => {
      setIsDisconnected(false);
      setErrorMessage('');
    };

    window.addEventListener('api_connection_error', handleConnectionError);
    window.addEventListener('api_connection_restored', handleConnectionRestored);

    return () => {
      window.removeEventListener('api_connection_error', handleConnectionError);
      window.removeEventListener('api_connection_restored', handleConnectionRestored);
    };
  }, []);

  const handleManualReconnect = async () => {
    setIsReconnecting(true);
    try {
      const res = await fetch('/api/v1/agent/clinic-rooms/selected', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`,
        },
      });
      if (res.status !== 502 && res.status !== 503 && res.status !== 504) {
        setIsDisconnected(false);
        setErrorMessage('');
        window.dispatchEvent(new CustomEvent('api_connection_restored'));
      }
    } catch {
      // Still disconnected
    } finally {
      setIsReconnecting(false);
    }
  };

  if (!isDisconnected) return null;

  return (
    <div className="fixed top-3 left-1/2 -translate-x-1/2 z-50 max-w-xl w-11/12 animate-in slide-in-from-top duration-200">
      <div className="flex items-center justify-between gap-3 px-4 py-2.5 rounded-2xl bg-amber-500/95 dark:bg-amber-900/95 backdrop-blur-md text-white shadow-xl border border-amber-400 dark:border-amber-700 text-xs">
        <div className="flex items-center gap-2.5 overflow-hidden">
          <span className="w-2.5 h-2.5 rounded-full bg-white animate-ping shrink-0" />
          <span className="font-semibold truncate">
            {errorMessage || 'Koneksi ke backend terputus. Mencoba menghubungkan kembali...'}
          </span>
        </div>

        <button
          type="button"
          onClick={handleManualReconnect}
          disabled={isReconnecting}
          className="px-3 py-1 rounded-xl bg-white/20 hover:bg-white/30 text-white font-bold text-[11px] shrink-0 transition-all active:scale-95 disabled:opacity-50"
        >
          {isReconnecting ? 'Menghubungkan...' : 'Hubungkan Ulang'}
        </button>
      </div>
    </div>
  );
}
