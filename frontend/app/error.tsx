'use client';

import { useEffect } from 'react';

export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error('Unhandled page error:', error);
  }, [error]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-emerald-50 p-6 text-emerald-950">
      <section className="w-full max-w-md rounded-2xl border border-emerald-200 bg-white p-8 text-center shadow-lg">
        <div className="mb-4 text-5xl">⚠️</div>
        <h1 className="text-2xl font-bold">Terjadi kesalahan</h1>
        <p className="mt-3 text-sm text-emerald-700">Halaman tidak dapat dimuat. Silakan coba kembali.</p>
        <button onClick={reset} className="mt-6 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500">
          Coba lagi
        </button>
      </section>
    </main>
  );
}
