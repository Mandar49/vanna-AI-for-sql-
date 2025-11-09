document.addEventListener('DOMContentLoaded', () => {
    const conversationList = document.getElementById('conversation-list');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatHistory = document.getElementById('chat-history');
    const askForm = document.getElementById('ask-form');
    const questionInput = document.getElementById('question-input');

    let currentConversationId = null;

    const loadConversations = async () => {
        const response = await fetch('/api/conversations');
        const conversations = await response.json();
        conversationList.innerHTML = '';
        conversations.forEach(conv => {
            const link = document.createElement('a');
            link.href = '#';
            link.dataset.id = conv.id;
            link.textContent = conv.title;
            if (conv.id === currentConversationId) {
                link.classList.add('active');
            }
            conversationList.appendChild(link);
        });
    };

    const renderChatHistory = (history) => {
        chatHistory.innerHTML = '';
        history.forEach(message => {
            const messageEl = document.createElement('div');
            messageEl.classList.add('message', message.role === 'user' ? 'user-message' : 'ai-message');

            if (message.role === 'assistant') {
                // For AI messages, render the value as Markdown
                messageEl.innerHTML = marked.parse(message.value);
            } else {
                // For user messages, just display the plain text
                const p = document.createElement('p');
                p.textContent = message.value;
                messageEl.appendChild(p);
            }

            if (message.sql) {
                const btn = document.createElement('button');
                btn.textContent = 'Show SQL';
                btn.classList.add('show-sql-btn');
                btn.onclick = () => {
                    const pre = messageEl.querySelector('pre');
                    if (pre) {
                        pre.style.display = pre.style.display === 'none' ? 'block' : 'none';
                    }
                };
                messageEl.appendChild(btn);

                const pre = document.createElement('pre');
                pre.classList.add('sql-code');
                pre.style.display = 'none';
                pre.textContent = message.sql;
                messageEl.appendChild(pre);
            }
            chatHistory.appendChild(messageEl);
        });
        chatHistory.scrollTop = chatHistory.scrollHeight;
    };

    const loadConversation = async (id) => {
        const response = await fetch(`/api/conversations/${id}`);
        const history = await response.json();
        currentConversationId = id;
        renderChatHistory(history);
        loadConversations();
    };

    const startNewChat = () => {
        currentConversationId = `conversation_${Date.now()}`;
        chatHistory.innerHTML = '';
        questionInput.value = '';
        questionInput.focus();
        loadConversations();
    };

    newChatBtn.addEventListener('click', startNewChat);

    conversationList.addEventListener('click', (e) => {
        if (e.target.tagName === 'A') {
            e.preventDefault();
            loadConversation(e.target.dataset.id);
        }
    });

    askForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = questionInput.value;
        if (!question) return;

        if (!currentConversationId) {
            startNewChat();
        }

        const userMessage = { role: 'user', 'value': question };
        const tempHistory = [...getCurrentHistory(), userMessage];
        renderChatHistory(tempHistory);

        questionInput.value = '';

        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                conversation_id: currentConversationId
            })
        });

        const updatedHistory = await response.json();
        renderChatHistory(updatedHistory);
        loadConversations();
    });

    const getCurrentHistory = () => {
        const history = [];
        document.querySelectorAll('#chat-history .message').forEach(msg => {
            const role = msg.classList.contains('user-message') ? 'user' : 'assistant';
            const value = msg.querySelector('p')?.textContent || msg.textContent;
            history.push({ role, value });
        });
        return history;
    };

    loadConversations();
    startNewChat();
});
