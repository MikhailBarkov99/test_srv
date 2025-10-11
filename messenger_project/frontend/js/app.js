import { Api } from './api.js';
import { Auth } from './auth.js';
import { ChatSocket } from './websocket.js';

const chatListEl = document.getElementById('chat-list');
const contactListEl = document.getElementById('contact-list');
const messageHistoryEl = document.getElementById('message-history');
const chatSection = document.getElementById('chat-section');
const authSection = document.getElementById('auth-section');
const chatHeaderEl = document.getElementById('chat-header');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const profileInfoEl = document.getElementById('profile-info');
const logoutBtn = document.getElementById('logout-btn');
const searchInput = document.getElementById('search-input');

let activeChat = null;
let socket = null;

async function loadChats() {
  const chats = await Api.listChats();
  chatListEl.innerHTML = chats.results
    .map(
      (chat) => `
        <div class="chat-item ${activeChat && activeChat.id === chat.id ? 'active' : ''}" data-id="${chat.id}">
          <h4>${chat.name || 'Untitled chat'}</h4>
          <p>${chat.last_message ? chat.last_message.content : 'No messages yet'}</p>
        </div>
      `,
    )
    .join('');
}

async function loadContacts(term = '') {
  const contacts = await Api.listContacts(term);
  contactListEl.innerHTML = contacts.results
    .map((user) => `<div class="contact-item">${user.username}</div>`)
    .join('');
}

async function loadProfile() {
  const profile = await Api.getProfile();
  profileInfoEl.innerHTML = `
    <strong>${profile.username}</strong>
    <p>${profile.bio || ''}</p>
    <small>Online: ${profile.is_online ? 'Yes' : 'No'}</small>
  `;
}

async function loadMessages(chatId) {
  const response = await Api.fetchMessages(chatId);
  messageHistoryEl.innerHTML = response.results
    .slice()
    .reverse()
    .map(
      (message) => `
        <div class="message ${message.sender.username === localStorage.getItem('username') ? 'self' : 'other'}">
          <div class="message-author">${message.sender.username}</div>
          <div class="message-content">${message.content}</div>
          <div class="message-time">${new Date(message.created_at).toLocaleTimeString()}</div>
        </div>
      `,
    )
    .join('');
  messageHistoryEl.scrollTop = messageHistoryEl.scrollHeight;
}

function openChat(chatId) {
  const chat = window.currentChats.find((item) => item.id === Number(chatId));
  if (!chat) return;
  activeChat = chat;
  chatHeaderEl.innerHTML = `<h2>${chat.name || 'Chat'}</h2>`;
  chatSection.classList.remove('hidden');
  authSection.classList.add('hidden');
  loadMessages(chat.id);
  socket = new ChatSocket(chat.id, (message) => {
    appendMessage(message);
  });
  socket.connect();
}

function appendMessage(message) {
  const div = document.createElement('div');
  div.classList.add('message');
  if (message.sender.username === localStorage.getItem('username')) {
    div.classList.add('self');
  } else {
    div.classList.add('other');
  }
  div.innerHTML = `
    <div class="message-author">${message.sender.username}</div>
    <div class="message-content">${message.content}</div>
    <div class="message-time">${new Date(message.created_at).toLocaleTimeString()}</div>
  `;
  messageHistoryEl.appendChild(div);
  messageHistoryEl.scrollTop = messageHistoryEl.scrollHeight;
}

async function bootstrap() {
  if (!Auth.isAuthenticated()) {
    authSection.classList.remove('hidden');
    chatSection.classList.add('hidden');
    return;
  }
  await Promise.all([loadProfile(), loadChats(), loadContacts()]);
  window.currentChats = (await Api.listChats()).results;
  chatListEl.addEventListener('click', (event) => {
    const item = event.target.closest('.chat-item');
    if (!item) return;
    openChat(item.dataset.id);
  });
}

window.addEventListener('auth:login', async () => {
  authSection.classList.add('hidden');
  chatSection.classList.remove('hidden');
  const profile = await Api.getProfile();
  localStorage.setItem('username', profile.username);
  await bootstrap();
});

window.addEventListener('auth:logout', () => {
  authSection.classList.remove('hidden');
  chatSection.classList.add('hidden');
  chatListEl.innerHTML = '';
  messageHistoryEl.innerHTML = '';
});

messageForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!activeChat) return;
  const content = messageInput.value.trim();
  if (!content) return;
  socket.send(content);
  messageInput.value = '';
});

logoutBtn.addEventListener('click', () => Auth.logout());

document.getElementById('login-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;
  try {
    await Auth.login(username, password);
  } catch (error) {
    alert(error.message);
  }
});

document.getElementById('register-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = {
    username: document.getElementById('register-username').value,
    email: document.getElementById('register-email').value,
    password: document.getElementById('register-password').value,
    password_confirm: document.getElementById('register-password-confirm').value,
  };
  try {
    await Auth.register(payload);
    alert('Registration successful. Please login.');
  } catch (error) {
    alert(error.message);
  }
});

searchInput.addEventListener('input', async (event) => {
  const term = event.target.value;
  window.currentChats = (await Api.searchChats(term)).results;
  await loadChats();
  await loadContacts(term);
});

bootstrap();
