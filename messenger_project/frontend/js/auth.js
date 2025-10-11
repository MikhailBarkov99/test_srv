import { Api } from './api.js';

export const Auth = {
  async login(username, password) {
    const tokens = await Api.login(username, password);
    localStorage.setItem('access', tokens.access);
    localStorage.setItem('refresh', tokens.refresh);
    window.dispatchEvent(new Event('auth:login'));
  },
  async logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.dispatchEvent(new Event('auth:logout'));
  },
  async register(data) {
    await Api.register(data);
  },
  isAuthenticated() {
    return Boolean(localStorage.getItem('access'));
  },
};
