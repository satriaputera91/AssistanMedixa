'use client';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export default function LoginPage() {
  const router = useRouter();
  const { login, error } = useAuth();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const email = form.get('email') as string;
    const password = form.get('password') as string;

    try {
      const data = await login(email, password);
      router.push(data.role === 'admin' ? '/admin' : '/doctor');
    } catch {
      // error state is handled by the hook
    }
  };

  const quickLogin = async (email: string, password: string) => {
    try {
      const data = await login(email, password);
      router.push(data.role === 'admin' ? '/admin' : '/doctor');
    } catch {
      // error state is handled by the hook
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-emerald-50 p-4 relative overflow-hidden">
      {/* Background Blurs */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-emerald-600/20 rounded-full blur-3xl" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-emerald-600/20 rounded-full blur-3xl" />

      <div className="w-full max-w-md bg-white/75 backdrop-blur-xl border border-white/[0.08] rounded-2xl p-8 shadow-2xl z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 text-[10px] font-semibold uppercase tracking-wider mb-4">
            📚 Dilengkapi Basis Pengetahuan Klinis
          </div>
          <h1 className="text-3xl font-extrabold text-emerald-950 mb-2">AssistantMedixa</h1>
          <p className="text-sm text-emerald-700">Platform AI Klinis Terintegrasi SIMRS / Satu Sehat</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-xs">
            {error}
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-emerald-800 mb-1">Alamat email</label>
            <input
              type="email"
              name="email"
              required
              placeholder="doctor@AssistantMedixa.com"
              className="w-full px-4 py-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-950 placeholder-emerald-400 focus:outline-none focus:border-emerald-500 transition-colors text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-emerald-800 mb-1">Kata sandi</label>
            <input
              type="password"
              name="password"
              required
              placeholder="••••••••"
              className="w-full px-4 py-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-950 placeholder-emerald-400 focus:outline-none focus:border-emerald-500 transition-colors text-sm"
            />
          </div>
          <button
            type="submit"
            className="w-full py-3 bg-gradient-to-r from-emerald-600 to-emerald-600 hover:from-emerald-500 hover:to-emerald-500 text-white font-semibold rounded-lg shadow-lg transition-all active:scale-[0.98] text-sm"
          >
            Masuk ke ruang kerja
          </button>
        </form>

        {/* Quick Demo Buttons */}
        <div className="mt-8 pt-6 border-t border-emerald-200 text-center">
          <p className="text-[10px] text-emerald-700 mb-3 uppercase tracking-wider">Akses demo cepat</p>
          <div className="flex gap-2">
            <button
              onClick={() => quickLogin('doctor@AssistantMedixa.com', 'doctor123')}
              className="flex-1 py-2 px-3 bg-emerald-100 hover:bg-emerald-200 text-xs font-medium text-emerald-900 rounded-lg border border-emerald-300 transition-colors"
            >
              🩺 Masuk Dokter
            </button>
            <button
              onClick={() => quickLogin('admin@AssistantMedixa.com', 'admin123')}
              className="flex-1 py-2 px-3 bg-emerald-100 hover:bg-emerald-200 text-xs font-medium text-emerald-900 rounded-lg border border-emerald-300 transition-colors"
            >
              ⚙️ Masuk Admin
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
