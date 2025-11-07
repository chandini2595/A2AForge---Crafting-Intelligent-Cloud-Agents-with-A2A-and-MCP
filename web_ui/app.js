const API_URL = 'http://localhost:8000';
let isLoading = false;

const messagesContainer = document.getElementById('messages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');

// Initialize
chatForm.addEventListener('submit', handleSubmit);

function handleSubmit(e) {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message) {
        sendMessage(message);
        messageInput.value = '';
    }
}

function sendQuickCommand(command) {
    if (!isLoading) {
        sendMessage(command);
    }
}

async function sendMessage(text) {
    if (isLoading) return;

    // Remove welcome message if it exists
    const welcome = messagesContainer.querySelector('.welcome');
    if (welcome) {
        welcome.remove();
    }

    // Add user message
    addMessage('user', text);

    // Show loading
    isLoading = true;
    setLoadingState(true);
    const loadingMsg = addLoadingMessage();

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();
        
        // Remove loading message
        loadingMsg.remove();

        // Add agent response
        addMessage('agent', data.response, data.success);

    } catch (error) {
        loadingMsg.remove();
        addMessage('agent', { 
            error: `Failed to connect to backend. Make sure the API is running on ${API_URL}` 
        }, false);
    } finally {
        isLoading = false;
        setLoadingState(false);
    }
}

function addMessage(role, content, success = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    headerDiv.textContent = role === 'user' ? '👤 You' : '🤖 Agent';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (role === 'user') {
        const p = document.createElement('p');
        p.textContent = content;
        contentDiv.appendChild(p);
    } else {
        contentDiv.appendChild(createResponseDisplay(content, success));
    }

    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    scrollToBottom();
}

function createResponseDisplay(data, success) {
    const responseDiv = document.createElement('div');
    responseDiv.className = 'response';

    if (data.error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = `❌ ${data.error}`;
        responseDiv.appendChild(errorDiv);
    } else if (data.message && typeof data.message === 'string') {
        const infoDiv = document.createElement('div');
        infoDiv.className = 'info';
        infoDiv.textContent = data.message;
        responseDiv.appendChild(infoDiv);
    } else {
        if (data.success) {
            const badge = document.createElement('div');
            badge.className = 'success-badge';
            badge.textContent = '✅ Success';
            responseDiv.appendChild(badge);
        }

        const pre = document.createElement('pre');
        pre.textContent = JSON.stringify(data, null, 2);
        responseDiv.appendChild(pre);
    }

    return responseDiv;
}

function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';

    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    headerDiv.textContent = '🤖 Agent';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.textContent = 'Processing...';

    contentDiv.appendChild(loadingDiv);
    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    scrollToBottom();
    return messageDiv;
}

function setLoadingState(loading) {
    messageInput.disabled = loading;
    const sendBtn = chatForm.querySelector('.send-btn');
    sendBtn.disabled = loading;

    const quickBtns = document.querySelectorAll('.quick-btn');
    quickBtns.forEach(btn => btn.disabled = loading);
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
