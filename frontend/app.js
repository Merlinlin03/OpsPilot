// randomUUID requires HTTPS or localhost; LAN HTTP must initialize too.
const sessionBytes = new Uint8Array(16);
window.crypto.getRandomValues(sessionBytes);
const senderId = `web-${Array.from(sessionBytes, (byte) => byte.toString(16).padStart(2, '0')).join('')}`;
let isLoading = false;

const categories = [
  {
    key: 'billing',
    title: '订阅与扣费',
    description: 'Premium 未开通、重复扣费',
    mark: '订',
    prompt: '我遇到了订阅或扣费问题。',
  },
  {
    key: 'crash',
    title: '崩溃与版本',
    description: 'App 闪退、更新异常',
    mark: '崩',
    prompt: '我的应用出现闪退问题。',
  },
  {
    key: 'ads',
    title: '广告体验',
    description: '广告过多、误触投诉',
    mark: '广',
    prompt: '我想反馈广告过多或误触的问题。',
  },
  {
    key: 'human',
    title: '申请人工协助',
    description: '申请升级处理',
    mark: '人',
    prompt: '这个问题我想转人工客服处理。',
  },
];


const messageList = document.querySelector('#message-list');
const chatForm = document.querySelector('#chat-form');
const messageInput = document.querySelector('#message-input');
const sendButton = document.querySelector('#send-button');
const categoryList = document.querySelector('#category-list');

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function renderCategories(activeKey) {
  categoryList.innerHTML = categories
    .map(
      (item) => `
        <button class="category-button ${item.key === activeKey ? 'active' : ''}" type="button" data-key="${item.key}">
          <span class="category-mark">${escapeHtml(item.mark)}</span>
          <span class="category-copy">
            <strong>${escapeHtml(item.title)}</strong>
            <span>${escapeHtml(item.description)}</span>
          </span>
        </button>
      `,
    )
    .join('');
}

function addMessage(role, text) {
  const row = document.createElement('div');
  row.className = `message-row ${role}`;
  row.innerHTML = `<div class="message-bubble">${escapeHtml(text)}</div>`;
  messageList.append(row);
  messageList.scrollTop = messageList.scrollHeight;
}

function setLoading(value) {
  isLoading = value;
  document.querySelector('#chat-status').textContent = value ? '正在回复...' : '';
  categoryList.querySelectorAll('button').forEach((button) => { button.disabled = value; });
  sendButton.disabled = isLoading;
  sendButton.innerHTML = isLoading ? '发送中...' : '发送 <span>→</span>';
  messageInput.disabled = isLoading;
}

async function sendMessage(text) {
  addMessage('user', text);
  setLoading(true);

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sender_id: senderId, text }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const messages = data.messages.length ? data.messages : [{ text: '后端没有返回消息。' }];
    messages.forEach((item) => addMessage('assistant', item.text || JSON.stringify(item.object)));
  } catch (error) {
    addMessage('assistant', `暂时无法获取回复（${error.message}），请稍后重试。`);
    messageInput.value = text;
  } finally {
    setLoading(false);
    messageInput.focus();
  }
}

function resetConversation() {
  messageList.innerHTML = '';
  addMessage(
    'assistant',
    '你好，我是 OpsPilot 智能客服。你遇到了什么问题？',
  );
}

categoryList.addEventListener('click', (event) => {
  const button = event.target.closest('[data-key]');

  if (!button || isLoading) {
    return;
  }

  const item = categories.find((category) => category.key === button.dataset.key);

  if (!item) {
    return;
  }

  renderCategories(item.key);
  messageInput.value = item.prompt;
  messageInput.focus();
});

chatForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();

  if (!text || isLoading) {
    return;
  }

  messageInput.value = '';
  sendMessage(text);
});

messageInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing && event.keyCode !== 229) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

renderCategories();
resetConversation();
