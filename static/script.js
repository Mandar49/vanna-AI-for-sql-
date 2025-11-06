document.addEventListener('DOMContentLoaded', () => {
    const conversationList = document.getElementById('conversation-list');
    const newChatBtn = document.getElementById('new-chat-btn');
    const askForm = document.getElementById('ask-form');
    const questionInput = document.getElementById('question-input');
    const chatHistory = document.getElementById('chat-history');

    let currentConversationId = null;

    // --- Core Functions ---

    const loadConversations = async () => {
        const response = await fetch('/api/conversations');
        const conversations = await response.json();
        conversationList.innerHTML = '';
        conversations.forEach(conv => {
            const link = document.createElement('a');
            link.href = '#';
            link.textContent = conv.title;
            link.dataset.id = conv.id;
            if (conv.id === currentConversationId) {
                link.classList.add('active');
            }
            conversationList.appendChild(link);
        });
    };

    const loadConversation = async (id) => {
        currentConversationId = id;
        const response = await fetch(`/api/conversations/${id}`);
        const history = await response.json();
        renderChatHistory(history);
        document.querySelectorAll('#conversation-list a').forEach(a => {
            a.classList.toggle('active', a.dataset.id === id);
        });
    };

    const renderChatHistory = (history) => {
        chatHistory.innerHTML = '';
        history.forEach(message => {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');

            if (message.role === 'user') {
                messageDiv.classList.add('user-message');
                messageDiv.textContent = message.value;
            } else {
                messageDiv.classList.add('ai-message');
                messageDiv.innerHTML = `<p>${message.value.replace(/\n/g, '<br>')}</p>`;

                if (message.sql) {
                    const showSqlBtn = document.createElement('button');
                    showSqlBtn.className = 'show-sql-btn';
                    showSqlBtn.textContent = 'Show SQL';

                    const sqlCode = document.createElement('div');
                    sqlCode.className = 'sql-code';
                    sqlCode.textContent = message.sql;
                    sqlCode.style.display = 'none';

                    showSqlBtn.onclick = () => {
                        const isHidden = sqlCode.style.display === 'none';
                        sqlCode.style.display = isHidden ? 'block' : 'none';
                        showSqlBtn.textContent = isHidden ? 'Hide SQL' : 'Show SQL';
                    };

                    messageDiv.appendChild(showSqlBtn);
                    messageDiv.appendChild(sqlCode);
                }
            }
            chatHistory.appendChild(messageDiv);
        });
        chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to bottom
    };

    const startNewChat = () => {
        currentConversationId = self.crypto.randomUUID();
        chatHistory.innerHTML = '';
        questionInput.value = '';
        questionInput.focus();
        loadConversations(); // To highlight the new "active" chat (which is none)
    };

    // --- Event Listeners ---

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

        // Add user message to UI immediately
        const userMessage = { role: 'user', value: question };
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
        loadConversations(); // Refresh list to show new title
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

    // --- Initial Load ---
    loadConversations();
    startNewChat();
});
