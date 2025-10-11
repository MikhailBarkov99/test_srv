/* eslint-disable no-undef */
/**
 * API utility functions for interacting with the messenger backend.
 */
const API_BASE_URL = '/api';
const ACCESS_TOKEN_KEY = 'messenger_access';
const REFRESH_TOKEN_KEY = 'messenger_refresh';

/**
 * Retrieve the stored access token.
 * @returns {string|null}
 */
export function getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Store authentication tokens in localStorage.
 * @param {string} access
 * @param {string} refresh
 */
export function setTokens(access, refresh) {
    if (access) {
        localStorage.setItem(ACCESS_TOKEN_KEY, access);
    }
    if (refresh) {
        localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
    }
}

/**
 * Remove tokens from storage.
 */
export function clearTokens() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * Retrieve the refresh token from storage.
 * @returns {string|null}
 */
export function getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Perform a fetch request with authentication headers.
 * @param {string} url
 * @param {RequestInit} options
 * @returns {Promise<Response>}
 */
export async function apiFetch(url, options = {}) {
    const accessToken = getAccessToken();
    const headers = new Headers(options.headers || {});
    if (!(options.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }

    if (accessToken) {
        headers.set('Authorization', `Bearer ${accessToken}`);
    }

    const requestOptions = {
        ...options,
        headers,
    };

    // Use fetch directly to keep compatibility with Django CSRF tokens for future extensions.
    const response = await fetch(`${API_BASE_URL}${url}`, requestOptions);
    if (response.status === 401 && getRefreshToken()) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            return apiFetch(url, options);
        }
    }
    return response;
}

/**
 * Authenticate a user and store the tokens.
 * @param {string} username
 * @param {string} password
 * @returns {Promise<object>}
 */
export async function login(username, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
        throw await response.json();
    }
    const data = await response.json();
    setTokens(data.access, data.refresh);
    return data;
}

/**
 * Register a new user.
 * @param {object} payload
 * @returns {Promise<object>}
 */
export async function register(payload) {
    const response = await fetch(`${API_BASE_URL}/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw await response.json();
    }
    return await response.json();
}

/**
 * Refresh the access token using the stored refresh token.
 * @returns {Promise<boolean>}
 */
export async function refreshAccessToken() {
    const refresh = getRefreshToken();
    if (!refresh) {
        return false;
    }
    const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
    });
    if (!response.ok) {
        clearTokens();
        return false;
    }
    const data = await response.json();
    setTokens(data.access, data.refresh || refresh);
    return true;
}

/**
 * Log the user out and clear stored tokens.
 * @returns {Promise<void>}
 */
export async function logout() {
    const refresh = getRefreshToken();
    if (refresh) {
        await fetch(`${API_BASE_URL}/auth/logout/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh }),
        });
    }
    clearTokens();
}

/**
 * Fetch the authenticated user's profile.
 * @returns {Promise<object>}
 */
export async function fetchCurrentUser() {
    const response = await apiFetch('/users/me/');
    if (!response.ok) {
        throw await response.json();
    }
    return await response.json();
}

/**
 * Update the authenticated user's profile.
 * @param {object} payload
 * @returns {Promise<object>}
 */
export async function updateProfile(payload) {
    const response = await apiFetch(`/users/${payload.id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw await response.json();
    }
    return await response.json();
}

/**
 * Retrieve the list of chats with optional search.
 * @param {string} search
 * @returns {Promise<object>}
 */
export async function fetchChats(search = '') {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    const response = await apiFetch(`/chats/${query}`);
    if (!response.ok) {
        throw await response.json();
    }
    return await response.json();
}

/**
 * Create a new chat.
 * @param {object} payload
 * @returns {Promise<object>}
 */
export async function createChat(payload) {
    const response = await apiFetch('/chats/', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw await response.json();
    }
    return await response.json();
}

/**
 * Fetch chat details including members.
 * @param {number} chatId
 * @returns {Promise<object>}
 */
export async function fetchChat(chatId) {
    const response = await apiFetch(`/chats/${chatId}/`);
    if (!response.ok) {
        throw await response.json();
    }
    return await response.json();
}

/**
 * Retrieve messages for a chat.
 * @param {number} chatId
 * @param {number} page
 * @returns {Promise<object>}
 */
export async function fetchChatMessages(chatId, page = 1) {
    const response = await apiFetch(`/chats/${chatId}/messages/?page=${page}`);
    if (!response.ok) {
        throw await response.json();
    }
    return await response.json();
}

/**
 * Send a message to a chat.
 * @param {FormData} formData
 * @returns {Promise<object>}
 */
export async function sendMessage(formData) {
    const response = await fetch(`${API_BASE_URL}/messages/`, {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${getAccessToken()}`,
        },
        body: formData,
    });
    if (!response.ok) {
        throw await response.json();
    }
    return await response.json();
}

/**
 * Mark a message as read.
 * @param {number} messageId
 * @returns {Promise<object>}
 */
export async function markMessageRead(messageId) {
    const response = await apiFetch(`/messages/${messageId}/read/`, {
        method: 'POST',
        body: JSON.stringify({ read: true }),
    });
    if (!response.ok) {
        throw await response.json();
    }
    return await response.json();
}
