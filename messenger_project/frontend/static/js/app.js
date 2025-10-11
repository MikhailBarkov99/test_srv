import {
    login,
    logout,
    register,
    fetchChats,
    fetchChat,
    fetchChatMessages,
    sendMessage,
    markMessageRead,
    fetchCurrentUser,
    updateProfile,
    getAccessToken,
    createChat,
} from './api.js';

let currentUser = null;
let chatsCache = [];

/**
 * Display a temporary message inside an element.
 * @param {HTMLElement} element
 * @param {string} message
 */
function showError(element, message) {
    if (!element) return;
    let text = message;
    if (typeof message === 'object' && message !== null) {
        text = Object.values(message).flat().join(' ');
    }
    element.textContent = text;
    element.classList.remove('d-none');
}

/**
 * Hide the provided error element.
 * @param {HTMLElement} element
 */
function hideError(element) {
    if (!element) return;
    element.classList.add('d-none');
}

/**
 * Update navigation UI depending on authentication state.
 */
function updateNavigation() {
    const navLogin = document.getElementById('nav-login');
    const logoutButton = document.getElementById('logout-button');
    if (!navLogin || !logoutButton) {
        return;
    }
    if (currentUser) {
        navLogin.classList.add('d-none');
        logoutButton.classList.remove('d-none');
    } else {
        navLogin.classList.remove('d-none');
        logoutButton.classList.add('d-none');
    }
}

/**
 * Attempt to load the authenticated user profile.
 */
async function bootstrapAuth() {
    if (!getAccessToken()) {
        updateNavigation();
        return;
    }
    try {
        currentUser = await fetchCurrentUser();
    } catch (error) {
        console.error('Failed to fetch current user', error);
        currentUser = null;
    }
    updateNavigation();
}

/**
 * Render chat list items.
 * @param {Array} chats
 */
function renderChats(chats) {
    const chatList = document.getElementById('chat-list');
    if (!chatList) return;
    chatList.innerHTML = '';
    chats.forEach((chat) => {
        const item = document.createElement('li');
        item.className = 'list-group-item list-group-item-action chat-item';
        item.dataset.chatId = chat.id;
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0">${chat.name}</h6>
                    <small class="text-muted">${chat.last_message ? chat.last_message.sender.username + ': ' + chat.last_message.content : 'No messages yet'}</small>
                </div>
                <span class="badge bg-secondary">${chat.is_group ? 'Group' : 'Direct'}</span>
            </div>`;
        chatList.appendChild(item);
    });
}

/**
 * Handle chat selection to show preview.
 * @param {Event} event
 */
async function handleChatSelection(event) {
    const item = event.target.closest('.chat-item');
    if (!item) return;
    const chatId = item.dataset.chatId;
    try {
        const chat = await fetchChat(chatId);
        document.getElementById('welcome-message')?.classList.add('d-none');
        const preview = document.getElementById('chat-preview');
        if (preview) {
            preview.classList.remove('d-none');
            const members = chat.members ? chat.members.map((m) => m.user.username).join(', ') : 'No members';
            document.getElementById('preview-chat-name').textContent = chat.name;
            document.getElementById('preview-chat-members').textContent = `Members: ${members}`;
            document.getElementById('open-chat-link').setAttribute('href', `/chat/${chat.id}/`);
        }
    } catch (error) {
        console.error('Failed to load chat preview', error);
    }
}

/**
 * Load chats from API and render them.
 * @param {string} search
 */
async function loadChats(search = '') {
    try {
        const data = await fetchChats(search);
        chatsCache = data.results || data;
        renderChats(chatsCache);
    } catch (error) {
        console.error('Failed to load chats', error);
    }
}

/**
 * Handle chat creation modal save.
 */
async function handleChatCreation() {
    const nameInput = document.getElementById('chat-name');
    const membersInput = document.getElementById('chat-members');
    const groupSwitch = document.getElementById('chat-is-group');
    const errorElement = document.getElementById('chat-error');
    hideError(errorElement);

    const payload = {
        name: nameInput.value.trim(),
        is_group: groupSwitch.checked,
        member_usernames: membersInput.value
            .split(',')
            .map((username) => username.trim())
            .filter(Boolean),
    };
    try {
        await createChat(payload);
        const modalElement = document.getElementById('chatModal');
        const modal = window.bootstrap ? window.bootstrap.Modal.getInstance(modalElement) || new window.bootstrap.Modal(modalElement) : null;
        modal?.hide();
        await loadChats();
        nameInput.value = '';
        membersInput.value = '';
        groupSwitch.checked = false;
    } catch (error) {
        showError(errorElement, error.detail || 'Unable to create chat.');
    }
}

/**
 * Populate chat detail page with data from API.
 * @param {number} chatId
 */
async function loadChatDetail(chatId) {
    try {
        const chat = await fetchChat(chatId);
        document.getElementById('chat-title').textContent = chat.name;
        const members = (chat.members || []).map((member) => member.user.username).join(', ');
        document.getElementById('chat-members-list').textContent = members || 'No members yet';
        await loadMessages(chatId);
    } catch (error) {
        const errorBox = document.getElementById('message-error');
        showError(errorBox, error.detail || 'Failed to load chat.');
    }
}

/**
 * Fetch messages for chat and render them.
 * @param {number} chatId
 * @param {number} page
 */
async function loadMessages(chatId, page = 1) {
    const container = document.getElementById('message-container');
    if (!container) return;
    container.innerHTML = '';
    try {
        const data = await fetchChatMessages(chatId, page);
        const messages = data.results || data;
        if (!messages.length) {
            container.innerHTML = '<p class="text-muted">No messages yet.</p>';
            return;
        }
        messages
            .slice()
            .reverse()
            .forEach((message) => {
                const messageElement = document.createElement('div');
                messageElement.className = `message ${message.sender.id === currentUser?.id ? 'message-outgoing' : 'message-incoming'}`;
                messageElement.innerHTML = `
                    <div class="message-header">
                        <strong>${message.sender.username}</strong>
                        <small class="text-muted ms-2">${new Date(message.created_at).toLocaleString()}</small>
                    </div>
                    <div class="message-body">${message.content || ''}</div>
                `;
                if (message.attachment) {
                    const link = document.createElement('a');
                    link.href = message.attachment;
                    link.textContent = 'Attachment';
                    link.target = '_blank';
                    messageElement.appendChild(link);
                }
                container.appendChild(messageElement);
                if (message.sender.id !== currentUser?.id) {
                    markMessageRead(message.id).catch((error) => console.warn('Failed to mark message read', error));
                }
            });
    } catch (error) {
        container.innerHTML = '<div class="alert alert-danger">Failed to load messages.</div>';
        console.error(error);
    }
}

/**
 * Handle message form submission.
 * @param {Event} event
 */
async function handleMessageSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const errorBox = document.getElementById('message-error');
    hideError(errorBox);
    const chatId = Number(form.closest('.row').dataset.chatId);
    const messageInput = document.getElementById('message-input');
    const attachmentInput = document.getElementById('message-attachment');

    const formData = new FormData();
    formData.append('chat', chatId);
    formData.append('content', messageInput.value.trim());
    if (attachmentInput.files[0]) {
        formData.append('attachment', attachmentInput.files[0]);
    }

    try {
        await sendMessage(formData);
        messageInput.value = '';
        attachmentInput.value = '';
        await loadMessages(chatId);
    } catch (error) {
        showError(errorBox, error.detail || 'Unable to send message.');
    }
}

/**
 * Handle profile update submission.
 * @param {Event} event
 */
async function handleProfileSubmit(event) {
    event.preventDefault();
    const alertBox = document.getElementById('profile-alert');
    hideError(alertBox);
    try {
        const payload = {
            id: currentUser.id,
            first_name: document.getElementById('profile-first-name').value,
            last_name: document.getElementById('profile-last-name').value,
            status_message: document.getElementById('profile-status').value,
        };
        currentUser = await updateProfile(payload);
        showError(alertBox, 'Profile updated successfully.');
        alertBox.classList.remove('alert-danger');
        alertBox.classList.add('alert-success');
    } catch (error) {
        alertBox.classList.remove('alert-success');
        alertBox.classList.add('alert-danger');
        showError(alertBox, error.detail || 'Unable to update profile.');
    }
}

/**
 * Populate profile form fields.
 */
function populateProfileForm() {
    if (!currentUser) return;
    document.getElementById('profile-username').value = currentUser.username;
    document.getElementById('profile-email').value = currentUser.email;
    document.getElementById('profile-first-name').value = currentUser.first_name || '';
    document.getElementById('profile-last-name').value = currentUser.last_name || '';
    document.getElementById('profile-status').value = currentUser.status_message || '';
}

/**
 * Initialize handlers for login page.
 */
function initLoginPage() {
    const form = document.getElementById('login-form');
    if (!form) return;
    const errorBox = document.getElementById('login-error');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        hideError(errorBox);
        try {
            await login(
                document.getElementById('login-username').value,
                document.getElementById('login-password').value,
            );
            window.location.href = '/';
        } catch (error) {
            showError(errorBox, error.detail || 'Invalid credentials.');
        }
    });
}

/**
 * Initialize register page.
 */
function initRegisterPage() {
    const form = document.getElementById('register-form');
    if (!form) return;
    const errorBox = document.getElementById('register-error');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        hideError(errorBox);
        const password = document.getElementById('register-password').value;
        const passwordConfirm = document.getElementById('register-password-confirm').value;
        if (password !== passwordConfirm) {
            showError(errorBox, 'Passwords do not match.');
            return;
        }
        const payload = {
            username: document.getElementById('register-username').value,
            email: document.getElementById('register-email').value,
            first_name: document.getElementById('register-first-name').value,
            last_name: document.getElementById('register-last-name').value,
            password,
            password_confirm: passwordConfirm,
        };
        try {
            await register(payload);
            window.location.href = '/login/';
        } catch (error) {
            showError(errorBox, error.detail || 'Unable to register.');
        }
    });
}

/**
 * Initialize the chat index page.
 */
function initIndexPage() {
    const chatList = document.getElementById('chat-list');
    if (!chatList) return;
    chatList.addEventListener('click', handleChatSelection);
    document.getElementById('chat-search-input').addEventListener('input', (event) => {
        loadChats(event.target.value);
    });
    document.getElementById('create-chat-button').addEventListener('click', () => {
        const modalElement = document.getElementById('chatModal');
        if (window.bootstrap) {
            const modal = window.bootstrap.Modal.getOrCreateInstance(modalElement);
            modal.show();
        }
    });
    document.getElementById('save-chat-button').addEventListener('click', handleChatCreation);
    loadChats();
}

/**
 * Initialize chat detail page.
 */
function initChatPage() {
    const messageForm = document.getElementById('message-form');
    if (!messageForm) return;
    const chatId = Number(document.querySelector('[data-chat-id]').dataset.chatId);
    messageForm.addEventListener('submit', handleMessageSubmit);
    loadChatDetail(chatId);
}

/**
 * Initialize profile page events.
 */
function initProfilePage() {
    const form = document.getElementById('profile-form');
    if (!form) return;
    populateProfileForm();
    form.addEventListener('submit', handleProfileSubmit);
}

/**
 * Register global logout handler.
 */
function initLogoutButton() {
    const button = document.getElementById('logout-button');
    if (!button) return;
    button.addEventListener('click', async () => {
        await logout();
        currentUser = null;
        updateNavigation();
        window.location.href = '/login/';
    });
}

/**
 * Entry point once the DOM is ready.
 */
async function init() {
    await bootstrapAuth();
    const path = window.location.pathname;
    const requiresAuth =
        path === '/' ||
        path === '/profile/' ||
        path === '/chat/' ||
        path.startsWith('/chat/');
    if (requiresAuth && !currentUser) {
        window.location.href = '/login/';
        return;
    }
    initLogoutButton();
    initLoginPage();
    initRegisterPage();
    initIndexPage();
    initChatPage();
    initProfilePage();
}

document.addEventListener('DOMContentLoaded', init);
