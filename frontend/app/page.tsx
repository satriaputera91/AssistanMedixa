'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AuthService } from '@/services/auth.service';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const token = AuthService.getToken();
    const role = AuthService.getUserRole();

    if (!token) {
      router.push('/login');
    } else if (role === 'admin') {
      router.push('/admin');
    } else {
      router.push('/doctor');
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center h-screen bg-emerald-50 text-emerald-700">
      <div className="text-center">
        <div className="text-4xl mb-3 animate-pulse">🏥</div>
        <p className="text-sm">Mengarahkan halaman…</p>
      </div>
    </div>
  );
}
