import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
import { login as apiLogin, getMe } from '../api/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  logout: () => {},
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      getMe()
        .then((data) => {
          console.log('User loaded:', data);
          setUser(data);
        })
        .catch((error) => {
          console.error('Failed to load user:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      console.log('Attempting login with:', email);
      
      // Call login API
      const loginResponse = await apiLogin(email, password);
      console.log('Login response:', loginResponse);
      
      // Store tokens
      localStorage.setItem('access_token', loginResponse.access_token);
      localStorage.setItem('refresh_token', loginResponse.refresh_token);
      
      // Get user data
      const userData = await getMe();
      console.log('User data:', userData);
      
      setUser(userData);
      
    } catch (error: any) {
      console.error('Login failed:', error);
      
      // Clear any stored tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Re-throw the error so Login component can show it
      throw new Error(error.response?.data?.detail || 'Error al iniciar sesión');
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};