import client from './client';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const login = async (email: string, password: string): Promise<LoginResponse> => {
  try {
    const response = await client.post('/auth/login', { 
      email, 
      password 
    });
    return response.data;
  } catch (error: any) {
    console.error('Login error:', error.response?.data || error.message);
    throw error;
  }
};

export const getMe = async () => {
  try {
    const response = await client.get('/auth/me');
    return response.data;
  } catch (error: any) {
    console.error('Get me error:', error.response?.data || error.message);
    throw error;
  }
};

export const refreshToken = async (refresh_token: string) => {
  try {
    const response = await client.post('/auth/refresh', { refresh_token });
    return response.data;
  } catch (error: any) {
    console.error('Refresh token error:', error.response?.data || error.message);
    throw error;
  }
};

export const logout = async () => {
  try {
    await client.post('/auth/logout');
  } catch (error: any) {
    console.error('Logout error:', error.response?.data || error.message);
  }
};