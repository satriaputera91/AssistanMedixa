import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-emerald-50 p-6 text-emerald-950">
      <section className="w-full max-w-md rounded-2xl border border-emerald-200 bg-white p-8 text-center shadow-lg">
        <div className="mb-4 text-5xl">🏥</div>
        <p className="text-sm font-semibold text-emerald-600">404</p>
        <h1 className="mt-1 text-2xl font-bold">Halaman tidak ditemukan</h1>
        <p className="mt-3 text-sm text-emerald-700">
          Tautan yang Anda buka tidak tersedia atau telah dipindahkan.
        </p>
        <Link
          href="/"
          className="mt-6 inline-flex rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-emerald-500"
        >
          Kembali ke beranda
        </Link>
      </section>
    </main>
  );
}
