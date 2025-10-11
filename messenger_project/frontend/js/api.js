const API_BASE = '/api/';
const AUTH_BASE = '/auth/';

function getAuthHeaders() {
  const token = localStorage.getItem('access');
  if (!token) {
    return {};
  }
  return {
    Authorization: `Bearer ${token}`,
  };
}

async function apiRequest(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
    ...getAuthHeaders(),
  };
  const response = await fetch(path.startsWith('http') ? path : `${API_BASE}${path}`, {
    ...options,
    headers,
  });
  if (response.status === 401) {
    window.dispatchEvent(new Event('auth:logout'));
    throw new Error('Unauthorized');
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
}

async function authRequest(path, payload) {
  const response = await fetch(`${AUTH_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Auth request failed');
  }
  return response.json();
}

export const Api = {
  async login(username, password) {
    return authRequest('token/', { username, password });
  },
  async refresh(refresh) {
    return authRequest('token/refresh/', { refresh });
  },
  async register(payload) {
    return authRequest('register/', payload);
  },
  async profile() {
    return apiRequest('chats/');
  },
  async getProfile() {
    return fetch(`${AUTH_BASE}me/`, { headers: getAuthHeaders() }).then((res) => res.json());
  },
  async updateProfile(data) {
    return fetch(`${AUTH_BASE}me/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data),
    }).then((res) => res.json());
  },
  async listChats() {
    return apiRequest('chats/');
  },
  async searchChats(term) {
    return apiRequest(`chats/search/?q=${encodeURIComponent(term)}`);
  },
  async listContacts(term = '') {
    return apiRequest(`contacts/?q=${encodeURIComponent(term)}`);
  },
  async fetchMessages(chatId) {
    return apiRequest(`messages/?chat=${chatId}`);
  },
  async sendMessage(chat, content) {
    return apiRequest('messages/', {
      method: 'POST',
      body: JSON.stringify({ chat, content }),
    });
  },
};
