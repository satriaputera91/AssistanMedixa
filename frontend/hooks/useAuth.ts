'use client';
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { AuthService } from '@/services/auth.service';

export type UserRole = 'doctor' | 'admin';

export function useAuth(requiredRole?: UserRole | UserRole[]) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userName, setUserName] = useState('');
  const [userRole, setUserRole] = useState<UserRole | ''>('');
  const [userEmail, setUserEmail] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = AuthService.getToken();
    const role = AuthService.getUserRole() as UserRole | null;

    if (!token) {
      setLoading(false);
      if (requiredRole) {
        router.push('/login');
      }
      return;
    }

    const isAllowed = !requiredRole || (
      Array.isArray(requiredRole)
        ? (role ? requiredRole.includes(role) : false)
        : role === requiredRole
    );

    if (!isAllowed) {
      setLoading(false);
      if (role === 'doctor') {
        router.push('/doctor');
      } else {
        router.push('/admin');
      }
      return;
    }

    setIsAuthenticated(true);
    setUserRole(role || '');
    setUserName(localStorage.getItem('user_name') || '');
    setUserEmail(localStorage.getItem('user_email') || '');
    setLoading(false);
  }, [requiredRole, router]);

  const login = useCallback(async (email: string, password: string) => {
    setError('');
    try {
      const data = await AuthService.login({ email, password });
      setIsAuthenticated(true);
      setUserName(data.name);
      setUserRole(data.role);
      setUserEmail(data.email);
      return data;
    } catch (err: any) {
      setError(err.message || 'Login gagal. Periksa email dan kata sandi Anda.');
      throw err;
    }
  }, []);

  const logout = useCallback(async () => {
    await AuthService.logout();
    setIsAuthenticated(false);
    setUserRole('');
    setUserName('');
    setUserEmail('');
    router.push('/login');
  }, [router]);

  return {
    isAuthenticated,
    userName,
    userRole,
    userEmail,
    loading,
    error,
    login,
    logout,
  };
}

