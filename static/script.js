document.addEventListener('DOMContentLoaded', () => {
    const conversationList = document.getElementById('conversation-list');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatHistory = document.getElementById('chat-history');
    const askForm = document.getElementById('ask-form');
    const questionInput = document.getElementById('question-input');
    const welcomeMessage = document.getElementById('welcome-message');

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
            link.className = 'block px-4 py-3 text-sm text-gray-700 dark:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-bg rounded-lg transition-colors duration-150 truncate';
            if (conv.id === currentConversationId) {
                link.className += ' bg-gray-100 dark:bg-dark-bg font-semibold';
            }
            conversationList.appendChild(link);
        });
    };

    const parseMetrics = (text) => {
        // Try to extract numeric values and labels from text
        const metrics = [];
        
        // Pattern 1: "Label: $X,XXX.XX" or "Label: X.XX%"
        const pattern1 = /([A-Za-z\s]+):\s*\$?([\d,]+\.?\d*)\s*%?/g;
        let match;
        while ((match = pattern1.exec(text)) !== null) {
            metrics.push({
                label: match[1].trim(),
                value: match[2],
                isCurrency: text.includes('$')
            });
        }
        
        // Pattern 2: Look for trend indicators
        const trendPattern = /(▲|▼|📈|📉|➖)\s*([\+\-]?\d+\.?\d*%?)/g;
        const trends = [];
        while ((match = trendPattern.exec(text)) !== null) {
            trends.push({
                icon: match[1],
                value: match[2]
            });
        }
        
        return { metrics, trends };
    };

    const createStyledCard = (label, value, trend = null) => {
        const card = document.createElement('div');
        card.className = 'stat-card bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-4 shadow-sm hover:shadow-md transition-all';
        
        const labelEl = document.createElement('h3');
        labelEl.className = 'text-sm font-medium text-gray-600 dark:text-dark-text-secondary uppercase tracking-wide mb-2';
        labelEl.textContent = label;
        
        const valueEl = document.createElement('p');
        valueEl.className = 'text-2xl font-bold text-gray-900 dark:text-dark-text mb-1';
        valueEl.textContent = value;
        
        card.appendChild(labelEl);
        card.appendChild(valueEl);
        
        if (trend) {
            const trendEl = document.createElement('span');
            const isPositive = trend.includes('▲') || trend.includes('📈') || trend.includes('+');
            const isNegative = trend.includes('▼') || trend.includes('📉') || trend.includes('-');
            
            trendEl.className = `text-sm font-medium ${
                isPositive ? 'text-green-600 dark:text-green-400' : 
                isNegative ? 'text-red-600 dark:text-red-400' : 
                'text-gray-600 dark:text-gray-400'
            }`;
            trendEl.textContent = trend;
            card.appendChild(trendEl);
        }
        
        return card;
    };

    const formatMessageContent = (text) => {
        // Check if message contains structured data that should be displayed as cards
        const lines = text.split('\n');
        const container = document.createElement('div');
        
        // Check for separator lines (plain text format)
        const hasSeparators = text.includes('────────');
        
        if (hasSeparators) {
            // Parse structured plain text format
            let currentSection = '';
            let sectionContent = [];
            
            lines.forEach(line => {
                if (line.includes('────────')) {
                    if (currentSection && sectionContent.length > 0) {
                        const section = createSection(currentSection, sectionContent.join('\n'));
                        container.appendChild(section);
                        sectionContent = [];
                    }
                } else if (line.trim() && !line.includes('────────')) {
                    if (!currentSection && line.trim().length > 0 && line === line.toUpperCase()) {
                        currentSection = line.trim();
                    } else {
                        sectionContent.push(line);
                    }
                }
            });
            
            // Add last section
            if (currentSection && sectionContent.length > 0) {
                const section = createSection(currentSection, sectionContent.join('\n'));
                container.appendChild(section);
            }
        } else {
            // Regular text formatting
            const p = document.createElement('p');
            p.className = 'text-gray-800 dark:text-dark-text whitespace-pre-wrap';
            p.textContent = text;
            container.appendChild(p);
        }
        
        return container;
    };

    const createSection = (title, content) => {
        const section = document.createElement('div');
        section.className = 'mb-4';
        
        if (title) {
            const titleEl = document.createElement('h3');
            titleEl.className = 'text-lg font-semibold text-gray-900 dark:text-dark-text mb-3 flex items-center';
            
            // Add icon based on section type
            const icon = getSectionIcon(title);
            if (icon) {
                titleEl.innerHTML = icon + ' ' + title;
            } else {
                titleEl.textContent = title;
            }
            
            section.appendChild(titleEl);
        }
        
        // Check if content looks like SQL
        if (content.trim().toUpperCase().startsWith('SELECT') || 
            content.trim().toUpperCase().startsWith('INSERT') ||
            content.trim().toUpperCase().startsWith('UPDATE')) {
            const pre = document.createElement('pre');
            pre.className = 'bg-gray-900 dark:bg-black text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono';
            pre.textContent = content.trim();
            section.appendChild(pre);
        } else {
            // Try to extract metrics for card display
            const { metrics } = parseMetrics(content);
            
            if (metrics.length > 0 && metrics.length <= 4) {
                // Display as cards
                const cardGrid = document.createElement('div');
                cardGrid.className = 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4';
                
                metrics.forEach(metric => {
                    const card = createStyledCard(
                        metric.label,
                        metric.isCurrency ? `$${metric.value}` : metric.value
                    );
                    cardGrid.appendChild(card);
                });
                
                section.appendChild(cardGrid);
            } else {
                // Regular text content
                const contentEl = document.createElement('div');
                contentEl.className = 'text-gray-700 dark:text-dark-text-secondary whitespace-pre-wrap bg-gray-50 dark:bg-dark-bg p-4 rounded-lg';
                contentEl.textContent = content.trim();
                section.appendChild(contentEl);
            }
        }
        
        return section;
    };

    const getSectionIcon = (title) => {
        const icons = {
            'SQL RESULT': '<svg class="w-5 h-5 inline mr-2 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path></svg>',
            'ANALYST': '<svg class="w-5 h-5 inline mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>',
            'STRATEGIST': '<svg class="w-5 h-5 inline mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>',
            'CAGR ANALYSIS': '<svg class="w-5 h-5 inline mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path></svg>',
            'SQL ERROR': '<svg class="w-5 h-5 inline mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
            'NO DATA FOUND': '<svg class="w-5 h-5 inline mr-2 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path></svg>'
        };
        return icons[title] || '';
    };

    const renderChatHistory = (history) => {
        chatHistory.innerHTML = '';
        
        if (history.length === 0) {
            // Show welcome message
            if (welcomeMessage) {
                chatHistory.appendChild(welcomeMessage.cloneNode(true));
            }
            return;
        }
        
        history.forEach(message => {
            const messageEl = document.createElement('div');
            messageEl.className = `flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`;

            const bubble = document.createElement('div');
            bubble.className = `max-w-3xl ${
                message.role === 'user' 
                    ? 'bg-accent text-white rounded-2xl rounded-tr-sm' 
                    : 'bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-2xl rounded-tl-sm'
            } px-5 py-4 shadow-sm`;

            if (message.role === 'user') {
                const p = document.createElement('p');
                p.className = 'text-white';
                p.textContent = message.value;
                bubble.appendChild(p);
            } else {
                // Parse and render as cards
                const cards = parseMessageToCards(message.value);
                cards.forEach(card => bubble.appendChild(card));

                if (message.sql) {
                    const sqlContainer = document.createElement('div');
                    sqlContainer.className = 'mt-4 flex gap-2 flex-wrap';
                    
                    const btn = document.createElement('button');
                    btn.textContent = 'Show SQL';
                    btn.className = 'text-sm px-3 py-1.5 bg-gray-100 dark:bg-dark-bg text-gray-700 dark:text-dark-text rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors';
                    
                    const pre = document.createElement('pre');
                    pre.className = 'hidden mt-3 w-full bg-gray-900 dark:bg-black text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono';
                    pre.textContent = message.sql;
                    
                    btn.onclick = () => {
                        pre.classList.toggle('hidden');
                        btn.textContent = pre.classList.contains('hidden') ? 'Show SQL' : 'Hide SQL';
                    };
                    
                    // Export dropdown
                    const exportContainer = document.createElement('div');
                    exportContainer.className = 'relative inline-block';
                    
                    const exportBtn = document.createElement('button');
                    exportBtn.innerHTML = `
                        <span class="flex items-center">
                            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            Export
                            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                            </svg>
                        </span>
                    `;
                    exportBtn.className = 'text-sm px-3 py-1.5 bg-accent text-white rounded-md hover:bg-accent-hover transition-colors';
                    
                    const exportMenu = document.createElement('div');
                    exportMenu.className = 'hidden absolute left-0 mt-2 w-32 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-md shadow-lg z-10';
                    exportMenu.innerHTML = `
                        <button class="export-option w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-bg transition-colors" data-format="csv">
                            📄 CSV
                        </button>
                        <button class="export-option w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-dark-text hover:bg-gray-100 dark:hover:bg-dark-bg transition-colors" data-format="pdf">
                            📕 PDF
                        </button>
                    `;
                    
                    exportBtn.onclick = (e) => {
                        e.stopPropagation();
                        exportMenu.classList.toggle('hidden');
                    };
                    
                    // Close menu when clicking outside
                    document.addEventListener('click', () => {
                        exportMenu.classList.add('hidden');
                    });
                    
                    // Handle export options
                    exportMenu.querySelectorAll('.export-option').forEach(option => {
                        option.onclick = async (e) => {
                            e.stopPropagation();
                            const format = option.dataset.format;
                            await exportMessage(message, format);
                            exportMenu.classList.add('hidden');
                        };
                    });
                    
                    exportContainer.appendChild(exportBtn);
                    exportContainer.appendChild(exportMenu);
                    
                    sqlContainer.appendChild(btn);
                    sqlContainer.appendChild(exportContainer);
                    sqlContainer.appendChild(pre);
                    bubble.appendChild(sqlContainer);
                }
            }

            messageEl.appendChild(bubble);
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
        if (welcomeMessage) {
            chatHistory.appendChild(welcomeMessage.cloneNode(true));
        }
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
        questionInput.disabled = true;
        askForm.querySelector('button').disabled = true;

        try {
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
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        } finally {
            questionInput.disabled = false;
            askForm.querySelector('button').disabled = false;
            questionInput.focus();
        }
    });

    const getCurrentHistory = () => {
        const history = [];
        document.querySelectorAll('#chat-history > div').forEach(msg => {
            const bubble = msg.querySelector('div');
            if (!bubble) return;
            
            const isUser = bubble.classList.contains('bg-accent');
            const role = isUser ? 'user' : 'assistant';
            const value = bubble.textContent.trim();
            
            if (value) {
                history.push({ role, value });
            }
        });
        return history;
    };

    // Export message function
    const exportMessage = async (message, format) => {
        try {
            // Get dark mode state
            const darkMode = document.documentElement.classList.contains('dark');
            
            // Find the question that led to this response
            const history = getCurrentHistory();
            const messageIndex = history.findIndex(m => m.role === 'assistant' && m.value.includes(message.value.substring(0, 50)));
            const question = messageIndex > 0 ? history[messageIndex - 1].value : 'Query';
            
            // Parse results from message (if it's a table)
            const results = parseResultsFromMessage(message.value);
            
            const exportData = {
                format: format,
                question: question,
                sql: message.sql || '',
                results: results,
                summary: message.value,
                dark_mode: darkMode
            };
            
            // Show loading state
            const loadingToast = showExportToast(`Exporting to ${format.toUpperCase()}...`, 'info');
            
            const response = await fetch('/api/export_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(exportData)
            });
            
            if (response.ok) {
                // Download the file
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `export_${Date.now()}.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                showExportToast(`✓ Exported to ${format.toUpperCase()} successfully!`, 'success');
            } else {
                const error = await response.json();
                showExportToast(`✗ Export failed: ${error.message}`, 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            showExportToast(`✗ Export failed: ${error.message}`, 'error');
        }
    };
    
    const parseResultsFromMessage = (messageText) => {
        // Try to extract table data from message
        // This is a simple parser - could be enhanced
        const results = [];
        
        // Look for table-like structures in the text
        // For now, return empty array - results will be fetched from actual query
        return results;
    };
    
    const showExportToast = (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-all ${
            type === 'success' ? 'bg-green-500 text-white' :
            type === 'error' ? 'bg-red-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
        
        return toast;
    };

    // Card rendering functions
    const parseMessageToCards = (messageText) => {
        const cards = [];
        
        // Check if message has structured sections
        const hasSeparators = messageText.includes('────────');
        
        if (hasSeparators) {
            // Parse structured format
            const sections = messageText.split(/─{40,}/);
            let currentSection = null;
            let currentContent = [];
            
            sections.forEach(section => {
                const lines = section.trim().split('\n');
                if (lines.length === 0) return;
                
                const firstLine = lines[0].trim();
                
                // Check if this is a section header
                if (firstLine && firstLine === firstLine.toUpperCase() && firstLine.length < 50) {
                    // Save previous section
                    if (currentSection) {
                        cards.push(createCard(currentSection, currentContent.join('\n')));
                    }
                    
                    currentSection = firstLine;
                    currentContent = lines.slice(1);
                } else {
                    currentContent.push(...lines);
                }
            });
            
            // Add last section
            if (currentSection) {
                cards.push(createCard(currentSection, currentContent.join('\n')));
            }
        } else {
            // No structured format - render as single insight card
            cards.push(createCard('Insight', messageText));
        }
        
        return cards;
    };
    
    const createCard = (title, content) => {
        // Determine card type
        let cardType = 'insight';
        if (title.includes('SQL') || title.includes('QUERY')) {
            cardType = 'sql';
        } else if (title.includes('DATA') || title.includes('RESULT')) {
            cardType = 'data';
        } else if (title.includes('ERROR')) {
            cardType = 'error';
        } else if (title.includes('STRATEGIST')) {
            cardType = 'strategist';
        }
        
        // Strip markdown
        content = stripMarkdown(content);
        
        // Create card element
        const card = document.createElement('div');
        card.className = `output-card output-card-${cardType}`;
        
        // Card header
        const header = document.createElement('div');
        header.className = 'output-card-header';
        header.style.cssText = 'display: flex; justify-content: space-between; align-items: center;';
        
        const titleEl = document.createElement('h3');
        titleEl.className = 'output-card-title';
        titleEl.textContent = title;
        header.appendChild(titleEl);
        
        // Collapse button for SQL
        if (cardType === 'sql') {
            const collapseBtn = document.createElement('button');
            collapseBtn.textContent = '▼';
            collapseBtn.className = 'collapse-btn';
            
            const contentEl = document.createElement('div');
            contentEl.className = 'output-card-content';
            contentEl.style.display = 'none';
            
            collapseBtn.onclick = () => {
                const isHidden = contentEl.style.display === 'none';
                contentEl.style.display = isHidden ? 'block' : 'none';
                collapseBtn.textContent = isHidden ? '▲' : '▼';
            };
            
            header.appendChild(collapseBtn);
            card.appendChild(header);
            
            // SQL content
            const pre = document.createElement('pre');
            pre.className = 'sql-code';
            pre.textContent = content;
            contentEl.appendChild(pre);
            card.appendChild(contentEl);
        } else {
            card.appendChild(header);
            
            // Card content
            const contentEl = document.createElement('div');
            contentEl.className = 'output-card-content';
            
            // Format content
            if (cardType === 'data') {
                contentEl.innerHTML = formatDataContent(content);
            } else {
                contentEl.innerHTML = formatTextContent(content);
            }
            
            card.appendChild(contentEl);
        }
        
        return card;
    };
    
    const stripMarkdown = (text) => {
        if (!text) return text;
        
        // Remove bold/italic
        text = text.replace(/\*\*\*(.+?)\*\*\*/g, '$1');
        text = text.replace(/\*\*(.+?)\*\*/g, '$1');
        text = text.replace(/\*(.+?)\*/g, '$1');
        text = text.replace(/__(.+?)__/g, '$1');
        text = text.replace(/_(.+?)_/g, '$1');
        
        // Remove headers
        text = text.replace(/^#{1,6}\s+/gm, '');
        
        // Remove code blocks
        text = text.replace(/```[\w]*\n/g, '');
        text = text.replace(/```/g, '');
        text = text.replace(/`(.+?)`/g, '$1');
        
        // Remove links
        text = text.replace(/\[(.+?)\]\(.+?\)/g, '$1');
        
        return text.trim();
    };
    
    const formatDataContent = (content) => {
        // Check if it looks like tabular data
        const lines = content.split('\n').filter(l => l.trim());
        
        if (lines.length > 1 && lines[0].includes('  ')) {
            // Looks like table data
            return `<pre style="font-family: monospace; font-size: 13px; white-space: pre-wrap; margin: 0; color: inherit;">${content}</pre>`;
        }
        
        return `<div style="font-family: monospace; font-size: 13px; color: inherit;">${content}</div>`;
    };
    
    const formatTextContent = (content) => {
        const lines = content.split('\n');
        const formatted = [];
        
        lines.forEach(line => {
            line = line.trim();
            if (!line) return;
            
            if (line.startsWith('- ') || line.startsWith('• ')) {
                formatted.push(`<li style="color: inherit;">${line.substring(2)}</li>`);
            } else if (line.endsWith(':') && line.length < 50) {
                formatted.push(`<div style="font-weight: 600; margin-top: 8px; color: inherit;">${line}</div>`);
            } else {
                formatted.push(`<p style="margin: 6px 0; color: inherit;">${line}</p>`);
            }
        });
        
        let html = formatted.join('');
        // Wrap consecutive list items in ul
        html = html.replace(/(<li.*?<\/li>\s*)+/g, '<ul style="margin: 8px 0; padding-left: 20px; color: inherit;">$&</ul>');
        
        return html;
    };
    
    // Toggle card function for collapsible cards
    window.toggleCard = (cardId) => {
        const card = document.getElementById(cardId);
        if (card) {
            card.style.display = card.style.display === 'none' ? 'block' : 'none';
        }
    };
    
    // Clear query cache function
    window.clearQueryCache = async () => {
        if (!confirm('Clear query cache? This will remove cached query history.')) {
            return;
        }
        
        try {
            const response = await fetch('/api/clear_cache', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                showExportToast('✓ Cache cleared successfully!', 'success');
            } else {
                showExportToast('✗ Failed to clear cache', 'error');
            }
        } catch (error) {
            console.error('Clear cache error:', error);
            showExportToast('✗ Error clearing cache', 'error');
        }
    };

    // Initialize
    loadConversations();
    startNewChat();
});
