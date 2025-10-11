import { Api } from './api.js';

export class ChatSocket {
  constructor(chatId, onMessage) {
    this.chatId = chatId;
    this.onMessage = onMessage;
    this.socket = null;
  }

  connect() {
    if (this.socket) {
      this.socket.close();
    }
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${window.location.host}/ws/chats/${this.chatId}/`;
    this.socket = new WebSocket(url);
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.onMessage(data);
    };
    this.socket.onclose = () => {
      setTimeout(() => this.connect(), 5000);
    };
  }

  send(content) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ content }));
    } else {
      Api.sendMessage(this.chatId, content);
    }
  }
}
