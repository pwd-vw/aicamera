import { defineStore } from 'pinia';
import api from '../utils/api';

interface UserProfile {
  id: string;
  email: string;
  username: string;
  role: string;
  firstName?: string;
  lastName?: string;
}

interface AuthState {
  token: string | null;
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('accessToken'),
    user: null,
    loading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (s) => Boolean(s.token),
    isAdmin: (s) => s.user?.role === 'admin',
  },
  actions: {
    setToken(token: string | null) {
      this.token = token;
      if (token) localStorage.setItem('accessToken', token);
      else localStorage.removeItem('accessToken');
    },
    async login(username: string, password: string) {
      this.loading = true; this.error = null;
      try {
        const { data } = await api.post('/auth/login', { username, password });
        this.setToken(data.accessToken || data.access_token || data.token);
        await this.fetchProfile();
        return true;
      } catch (e: any) {
        this.error = e?.response?.data?.message || 'Login failed';
        this.setToken(null);
        return false;
      } finally {
        this.loading = false;
      }
    },
    async fetchProfile() {
      try {
        const { data } = await api.get('/auth/profile');
        this.user = data?.data || data; // support our API wrapper
      } catch (e) {
        this.user = null;
      }
    },
    async fetchUser() {
      // Alias for fetchProfile for consistency
      return await this.fetchProfile();
    },
    async logout() {
      try { await api.post('/auth/logout'); } catch {}
      this.user = null;
      this.setToken(null);
    },
  },
});
