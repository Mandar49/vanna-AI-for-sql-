"""
Executive Intelligence Layer - Dashboard Gateway (Phase 4A)
Minimal offline web dashboard for executive intelligence.
Provides quick access to profiles, reports, and voice summaries.
"""

from flask import Blueprint, render_template_string, jsonify, request, send_file
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Create Blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Login HTML template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Executive Intelligence Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .login-header p {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            color: #2c3e50;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ecf0f1;
            border-radius: 5px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn-login {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn-login:hover {
            background: #5568d3;
        }
        
        .error-message {
            background: #e74c3c;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: none;
        }
        
        .info-message {
            background: #3498db;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🎯 Executive Intelligence</h1>
            <p>Offline AI Business Intelligence System</p>
        </div>
        
        <div id="error" class="error-message"></div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn-login">Login</button>
        </form>
        
        <div class="info-message">
            <strong>Default Credentials:</strong><br>
            Username: admin | Password: admin123<br>
            <small>Change password after first login</small>
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('error');
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Store token in cookie
                    document.cookie = `auth_token=${data.token}; path=/; max-age=86400`;
                    // Redirect to dashboard
                    window.location.href = '/dashboard/';
                } else {
                    errorDiv.textContent = data.message;
                    errorDiv.style.display = 'block';
                }
            } catch (error) {
                errorDiv.textContent = 'Login failed: ' + error.message;
                errorDiv.style.display = 'block';
            }
        });
    </script>
</body>
</html>
"""

# Dashboard HTML template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Intelligence Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #7f8c8d;
            font-size: 16px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .stat-card h3 {
            color: #7f8c8d;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            color: #2c3e50;
            font-size: 36px;
            font-weight: bold;
        }
        
        .stat-card .label {
            color: #95a5a6;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .section {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            color: #2c3e50;
            font-size: 24px;
            margin-bottom: 20px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        
        .profile-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .profile-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
        }
        
        .profile-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-color: #667eea;
        }
        
        .profile-card.active {
            background: #667eea;
            color: white;
        }
        
        .profile-card h3 {
            font-size: 18px;
            margin-bottom: 5px;
        }
        
        .profile-card .persona {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .profile-card .count {
            font-size: 12px;
            margin-top: 10px;
            opacity: 0.7;
        }
        
        .report-list {
            list-style: none;
        }
        
        .report-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .report-item:hover {
            background: #e9ecef;
        }
        
        .report-name {
            font-weight: 500;
            color: #2c3e50;
        }
        
        .report-date {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: #5568d3;
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: #95a5a6;
        }
        
        .btn-secondary:hover {
            background: #7f8c8d;
        }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .voice-controls {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .voice-controls h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .status.online {
            background: #2ecc71;
            color: white;
        }
        
        .status.offline {
            background: #e74c3c;
            color: white;
        }
        
        /* Data Validation Panel Styles */
        .validation-panel {
            position: fixed;
            right: -400px;
            top: 0;
            width: 400px;
            height: 100vh;
            background: white;
            box-shadow: -4px 0 10px rgba(0,0,0,0.1);
            transition: right 0.3s ease;
            z-index: 1000;
            overflow-y: auto;
        }
        
        .validation-panel.open {
            right: 0;
        }
        
        .validation-header {
            background: #667eea;
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .validation-header h2 {
            margin: 0;
            font-size: 20px;
        }
        
        .close-panel {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
        }
        
        .validation-content {
            padding: 20px;
        }
        
        .validation-item {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .validation-item:last-child {
            border-bottom: none;
        }
        
        .validation-label {
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        .validation-value {
            font-size: 16px;
            color: #2c3e50;
            font-weight: 500;
        }
        
        .validation-value.code {
            font-family: 'Courier New', monospace;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            font-size: 13px;
            word-break: break-all;
            max-height: 150px;
            overflow-y: auto;
        }
        
        .refresh-btn {
            width: 100%;
            background: #2ecc71;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .refresh-btn:hover {
            background: #27ae60;
        }
        
        .refresh-btn:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        
        .toggle-panel-btn {
            position: fixed;
            right: 20px;
            top: 20px;
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 999;
            transition: all 0.3s;
        }
        
        .toggle-panel-btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }
        
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #2ecc71;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            z-index: 2000;
            opacity: 0;
            transform: translateY(-20px);
            transition: all 0.3s;
        }
        
        .toast.show {
            opacity: 1;
            transform: translateY(0);
        }
        
        .toast.error {
            background: #e74c3c;
        }
    </style>
</head>
<body>
    <!-- Toggle Panel Button -->
    <button class="toggle-panel-btn" onclick="toggleValidationPanel()">
        📊 Data Validation
    </button>
    
    <!-- Data Validation Panel -->
    <div class="validation-panel" id="validationPanel">
        <div class="validation-header">
            <h2>Data Validation</h2>
            <button class="close-panel" onclick="toggleValidationPanel()">×</button>
        </div>
        <div class="validation-content">
            <div class="validation-item">
                <div class="validation-label">Active Database</div>
                <div class="validation-value" id="dbName">Loading...</div>
            </div>
            
            <div class="validation-item">
                <div class="validation-label">Tables Loaded</div>
                <div class="validation-value" id="tableCount">Loading...</div>
            </div>
            
            <div class="validation-item">
                <div class="validation-label">Last SQL Executed</div>
                <div class="validation-value code" id="lastSQL">No query executed yet</div>
            </div>
            
            <div class="validation-item">
                <div class="validation-label">Execution Time</div>
                <div class="validation-value" id="execTime">N/A</div>
            </div>
            
            <button class="refresh-btn" onclick="refreshSchema()" id="refreshBtn">
                <span>🔄</span>
                <span>Refresh Schema</span>
            </button>
        </div>
    </div>
    
    <!-- Toast Notification -->
    <div class="toast" id="toast"></div>
    
    <div class="container">
        <div class="header">
            <h1>🎯 Executive Intelligence Dashboard</h1>
            <p>Offline AI Business Intelligence System</p>
            <div style="margin-top: 10px;">
                <span class="status online">● OFFLINE MODE</span>
                {% if current_user %}
                <span style="margin-left: 20px; color: #2c3e50;">
                    Active user: <strong>{{ current_user.username }}</strong> ({{ current_user.role }})
                </span>
                {% endif %}
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Active Profile</h3>
                <div class="value">{{ active_profile or 'None' }}</div>
                <div class="label">Current Context</div>
            </div>
            
            <div class="stat-card">
                <h3>Total Profiles</h3>
                <div class="value">{{ profiles|length }}</div>
                <div class="label">Departments</div>
            </div>
            
            <div class="stat-card">
                <h3>Reports Generated</h3>
                <div class="value">{{ reports|length }}</div>
                <div class="label">Available Reports</div>
            </div>
            
            <div class="stat-card">
                <h3>System Status</h3>
                <div class="value">✓</div>
                <div class="label">Operational</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Department Profiles</h2>
            <div class="profile-list">
                {% for profile in profiles %}
                <div class="profile-card {% if profile.name == active_profile %}active{% endif %}"
                     onclick="activateProfile('{{ profile.name }}')">
                    <h3>{{ profile.name }}</h3>
                    <div class="persona">{{ profile.persona }}</div>
                    <div class="count">{{ profile.interaction_count }} interactions</div>
                </div>
                {% endfor %}
            </div>
            
            <div class="voice-controls">
                <h3>🎙 Voice Controls</h3>
                <div class="actions">
                    <button class="btn" onclick="speakSummary()">Speak Summary</button>
                    <button class="btn btn-secondary" onclick="generateReport()">Generate Report</button>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📚 Knowledge Base</h2>
            <div class="voice-controls">
                <h3>📄 Document Management</h3>
                <div class="actions">
                    <input type="file" id="documentUpload" style="display: none;" onchange="uploadDocument()">
                    <button class="btn" onclick="document.getElementById('documentUpload').click()">Upload Document</button>
                    <button class="btn btn-secondary" onclick="listDocuments()">List Documents</button>
                </div>
                <div id="uploadStatus" style="margin-top: 15px; display: none;"></div>
                <div id="documentList" style="margin-top: 15px;"></div>
            </div>
            
            <div class="voice-controls" style="margin-top: 20px;">
                <h3>🔍 Search Knowledge</h3>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="searchQuery" placeholder="Enter search query..." 
                           style="flex: 1; padding: 10px; border: 2px solid #ecf0f1; border-radius: 5px;">
                    <button class="btn" onclick="searchKnowledge()">Search</button>
                </div>
                <div id="searchResults" style="margin-top: 15px;"></div>
            </div>
        </div>
        
        <div class="section">
            <h2>📄 Recent Reports</h2>
            <ul class="report-list">
                {% for report in reports[:10] %}
                <li class="report-item">
                    <div>
                        <div class="report-name">{{ report.name }}</div>
                        <div class="report-date">{{ report.date }}</div>
                    </div>
                    <div class="actions">
                        <button class="btn" onclick="viewReport('{{ report.path }}')">View</button>
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>
    </div>
    
    <script>
        function activateProfile(profileName) {
            fetch(`/api/profiles/${profileName}/activate`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        }
        
        function speakSummary() {
            const activeProfile = '{{ active_profile }}';
            if (!activeProfile || activeProfile === 'None') {
                alert('Please activate a profile first');
                return;
            }
            
            fetch(`/dashboard/speak_summary?profile=${activeProfile}`)
            .then(response => response.json())
            .then(data => {
                alert(data.message || 'Summary generated');
            });
        }
        
        function generateReport() {
            const activeProfile = '{{ active_profile }}';
            if (!activeProfile || activeProfile === 'None') {
                alert('Please activate a profile first');
                return;
            }
            
            fetch(`/dashboard/run_report?profile=${activeProfile}`)
            .then(response => response.json())
            .then(data => {
                alert(data.message || 'Report generated');
                location.reload();
            });
        }
        
        function viewReport(path) {
            window.open(path, '_blank');
        }
        
        function uploadDocument() {
            const fileInput = document.getElementById('documentUpload');
            const file = fileInput.files[0];
            
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            const statusDiv = document.getElementById('uploadStatus');
            statusDiv.style.display = 'block';
            statusDiv.innerHTML = '<div style="color: #3498db;">Uploading...</div>';
            
            fetch('/dashboard/upload_knowledge', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    statusDiv.innerHTML = `<div style="color: #2ecc71;">✓ ${data.message}</div>`;
                    setTimeout(() => {
                        statusDiv.style.display = 'none';
                        listDocuments();
                    }, 2000);
                } else {
                    statusDiv.innerHTML = `<div style="color: #e74c3c;">✗ ${data.message}</div>`;
                }
            })
            .catch(error => {
                statusDiv.innerHTML = `<div style="color: #e74c3c;">✗ Upload failed: ${error.message}</div>`;
            });
            
            fileInput.value = '';
        }
        
        function listDocuments() {
            fetch('/dashboard/list_knowledge')
            .then(response => response.json())
            .then(data => {
                const listDiv = document.getElementById('documentList');
                
                if (data.documents && data.documents.length > 0) {
                    let html = '<div style="margin-top: 10px;"><strong>Documents in Knowledge Base:</strong><ul style="margin-top: 10px;">';
                    data.documents.forEach(doc => {
                        html += `<li style="padding: 5px 0;">${doc.filename} (${doc.chunk_count} chunks)</li>`;
                    });
                    html += '</ul></div>';
                    listDiv.innerHTML = html;
                } else {
                    listDiv.innerHTML = '<div style="margin-top: 10px; color: #7f8c8d;">No documents in knowledge base</div>';
                }
            })
            .catch(error => {
                console.error('List documents failed:', error);
            });
        }
        
        function searchKnowledge() {
            const query = document.getElementById('searchQuery').value;
            
            if (!query) {
                alert('Please enter a search query');
                return;
            }
            
            const resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = '<div style="color: #3498db;">Searching...</div>';
            
            fetch(`/dashboard/search_knowledge?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.results && data.results.length > 0) {
                    let html = '<div style="margin-top: 10px;"><strong>Search Results:</strong>';
                    data.results.forEach((result, i) => {
                        html += `
                            <div style="background: #f8f9fa; padding: 15px; margin-top: 10px; border-radius: 5px;">
                                <div style="font-weight: bold; margin-bottom: 5px;">${i+1}. ${result.source}</div>
                                <div style="color: #2c3e50;">${result.text}</div>
                                <div style="color: #7f8c8d; font-size: 12px; margin-top: 5px;">
                                    Relevance: ${(result.relevance * 100).toFixed(1)}%
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    resultsDiv.innerHTML = html;
                } else {
                    resultsDiv.innerHTML = '<div style="margin-top: 10px; color: #7f8c8d;">No results found</div>';
                }
            })
            .catch(error => {
                resultsDiv.innerHTML = `<div style="color: #e74c3c;">Search failed: ${error.message}</div>`;
            });
        }
        
        // Load documents on page load
        window.addEventListener('load', () => {
            listDocuments();
            loadValidationData();
        });
        
        // Data Validation Panel Functions
        function toggleValidationPanel() {
            const panel = document.getElementById('validationPanel');
            panel.classList.toggle('open');
        }
        
        function showToast(message, isError = false) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast show' + (isError ? ' error' : '');
            
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
        
        function loadValidationData() {
            fetch('/dashboard/validation_data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('dbName').textContent = data.database || 'N/A';
                    document.getElementById('tableCount').textContent = data.table_count || '0';
                    document.getElementById('lastSQL').textContent = data.last_sql || 'No query executed yet';
                    document.getElementById('execTime').textContent = data.execution_time || 'N/A';
                })
                .catch(error => {
                    console.error('Failed to load validation data:', error);
                });
        }
        
        function refreshSchema() {
            const btn = document.getElementById('refreshBtn');
            btn.disabled = true;
            btn.innerHTML = '<span>⏳</span><span>Refreshing...</span>';
            
            fetch('/dashboard/refresh_schema', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Schema reloaded successfully!');
                    loadValidationData();
                } else {
                    showToast(data.message || 'Failed to refresh schema', true);
                }
            })
            .catch(error => {
                showToast('Error: ' + error.message, true);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = '<span>🔄</span><span>Refresh Schema</span>';
            });
        }
    </script>
</body>
</html>
"""


@dashboard_bp.route('/')
def dashboard_home():
    """Main dashboard view."""
    try:
        from profile_manager import list_profiles, get_active_profile
        from auth_manager import get_current_user
        from flask import request
        
        # Check authentication
        token = request.cookies.get('auth_token')
        user = get_current_user(token) if token else None
        
        if not user:
            # Show login screen
            return render_template_string(LOGIN_TEMPLATE)
        
        # Get profiles
        profiles = list_profiles()
        active_profile = get_active_profile()
        
        # Get recent reports
        reports = get_recent_reports()
        
        return render_template_string(
            DASHBOARD_TEMPLATE,
            profiles=profiles,
            active_profile=active_profile,
            reports=reports,
            current_user=user
        )
    except Exception as e:
        return f"Dashboard error: {e}", 500


@dashboard_bp.route('/reports')
def dashboard_reports():
    """List all available reports."""
    try:
        reports = get_recent_reports()
        return jsonify({
            "success": True,
            "reports": reports
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/speak_summary')
def speak_summary():
    """Generate and speak a profile summary."""
    try:
        from voice_interface import summarize_conversation
        
        profile = request.args.get('profile')
        if not profile:
            return jsonify({"error": "Profile parameter required"}), 400
        
        summary = summarize_conversation(profile, speak=True)
        
        if summary:
            return jsonify({
                "success": True,
                "message": f"Summary generated for {profile}",
                "summary": summary
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Could not generate summary for {profile}"
            }), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/run_report')
def run_report():
    """Manually trigger report generation for a profile."""
    try:
        from report_generator import build_executive_report
        from profile_manager import load_recent
        import pandas as pd
        
        profile = request.args.get('profile')
        if not profile:
            return jsonify({"error": "Profile parameter required"}), 400
        
        # Load recent interactions
        recent = load_recent(profile, n=10)
        
        if not recent:
            return jsonify({
                "success": False,
                "message": f"No data available for {profile}"
            }), 404
        
        # Create summary DataFrame
        df = pd.DataFrame({
            "Metric": ["Total Interactions", "Recent Queries", "Profile Status"],
            "Value": [len(recent), min(10, len(recent)), "Active"]
        })
        
        # Generate report
        report = build_executive_report(
            title=f"{profile} Profile Summary - {datetime.now().strftime('%Y-%m-%d')}",
            question=f"What is the activity summary for {profile}?",
            sql="-- Profile context query",
            df=df,
            insights=f"Profile {profile} has {len(recent)} total interactions. Recent activity shows consistent engagement.",
            charts=None
        )
        
        return jsonify({
            "success": True,
            "message": f"Report generated for {profile}",
            "report_path": report['paths']['html_path']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/orchestration')
def orchestration_history():
    """View orchestration history."""
    try:
        from orchestrator import get_orchestration_history
        
        history = get_orchestration_history(limit=20)
        
        return jsonify({
            "success": True,
            "history": history
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/upload_knowledge', methods=['POST'])
def upload_knowledge():
    """Upload a document to the knowledge base."""
    try:
        from knowledge_fusion import ingest_document
        from werkzeug.utils import secure_filename
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "message": "No file provided"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "message": "No file selected"
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_dir = "./knowledge/uploads"
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)
        
        # Ingest document
        result = ingest_document(filepath, metadata={
            "uploaded_at": datetime.now().isoformat(),
            "original_filename": file.filename
        })
        
        return jsonify({
            "success": result["success"],
            "message": result["message"],
            "chunks": result.get("chunks", 0)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Upload failed: {str(e)}"
        }), 500


@dashboard_bp.route('/list_knowledge')
def list_knowledge():
    """List all documents in the knowledge base."""
    try:
        from knowledge_fusion import list_documents, get_knowledge_stats
        
        documents = list_documents()
        stats = get_knowledge_stats()
        
        return jsonify({
            "success": True,
            "documents": documents,
            "stats": stats
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"List failed: {str(e)}"
        }), 500


@dashboard_bp.route('/search_knowledge')
def search_knowledge_endpoint():
    """Search the knowledge base."""
    try:
        from knowledge_fusion import search_knowledge
        
        query = request.args.get('query')
        top_k = int(request.args.get('top_k', 5))
        
        if not query:
            return jsonify({
                "success": False,
                "message": "Query parameter required"
            }), 400
        
        results = search_knowledge(query, top_k=top_k)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result["text"],
                "source": result["metadata"].get("filename", "unknown"),
                "relevance": 1.0 - (result["distance"] if result["distance"] else 0)
            })
        
        return jsonify({
            "success": True,
            "results": formatted_results,
            "count": len(results),
            "query": query
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Search failed: {str(e)}"
        }), 500


@dashboard_bp.route('/validation_data')
def get_validation_data():
    """Get current database validation data."""
    try:
        from common import vn
        import mysql.connector
        
        # Get database connection info
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'ad_ai_testdb'
        }
        
        validation_data = {
            'database': db_config['database'],
            'table_count': 0,
            'last_sql': 'No query executed yet',
            'execution_time': 'N/A'
        }
        
        try:
            # Connect and get table count
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            validation_data['table_count'] = len(tables)
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Database connection error: {e}")
        
        # Try to get last SQL from error log or memory
        try:
            from error_logger import error_logger
            recent_errors = error_logger.get_recent_errors(n=1)
            if recent_errors:
                # Parse last SQL from error log
                error_text = recent_errors[0]
                if 'SQL Query:' in error_text:
                    sql_start = error_text.find('SQL Query:') + len('SQL Query:')
                    sql_end = error_text.find('\n\n', sql_start)
                    if sql_end > sql_start:
                        validation_data['last_sql'] = error_text[sql_start:sql_end].strip()
        except Exception:
            pass
        
        return jsonify(validation_data)
        
    except Exception as e:
        return jsonify({
            'database': 'Error',
            'table_count': 0,
            'last_sql': str(e),
            'execution_time': 'N/A'
        }), 500


@dashboard_bp.route('/refresh_schema', methods=['POST'])
def refresh_schema():
    """Refresh database schema by re-reading tables."""
    try:
        from common import vn
        import mysql.connector
        
        # Database connection info
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'ad_ai_testdb'
        }
        
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_count = len(tables)
        
        # Get table schemas
        schema_info = []
        for (table_name,) in tables:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            schema_info.append({
                'table': table_name,
                'columns': [col[0] for col in columns]
            })
        
        cursor.close()
        conn.close()
        
        # Re-train Vanna with schema information (if needed)
        # This would typically involve calling vn.train() with DDL statements
        # For now, we just verify the schema is accessible
        
        return jsonify({
            'success': True,
            'message': f'Schema refreshed successfully. Found {table_count} tables.',
            'table_count': table_count,
            'tables': [s['table'] for s in schema_info]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to refresh schema: {str(e)}'
        }), 500


def get_recent_reports(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get list of recent reports from the reports directory.
    
    Args:
        limit: Maximum number of reports to return
        
    Returns:
        List of report dictionaries
    """
    reports = []
    reports_dir = "./reports"
    
    if not os.path.exists(reports_dir):
        return reports
    
    # Scan for HTML and MD files
    for filename in os.listdir(reports_dir):
        if filename.endswith(('.html', '.md')):
            filepath = os.path.join(reports_dir, filename)
            
            # Get file stats
            stat = os.stat(filepath)
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            reports.append({
                "name": filename,
                "path": filepath,
                "date": modified_time.strftime("%Y-%m-%d %H:%M"),
                "size": stat.st_size,
                "type": "HTML" if filename.endswith('.html') else "Markdown"
            })
    
    # Sort by date (newest first)
    reports.sort(key=lambda x: x['date'], reverse=True)
    
    return reports[:limit]


if __name__ == "__main__":
    print("="*70)
    print("DASHBOARD GATEWAY TEST")
    print("="*70)
    print()
    
    print("Dashboard Blueprint created")
    print("Available routes:")
    print("  • /dashboard - Main dashboard view")
    print("  • /dashboard/reports - List reports")
    print("  • /dashboard/speak_summary?profile=<name> - Speak summary")
    print("  • /dashboard/run_report?profile=<name> - Generate report")
    print()
    
    print("="*70)
    print("✅ Dashboard Gateway ready")
    print("="*70)


# Analytics Hub Template
ANALYTICS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Hub - Executive Intelligence</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 16px;
            opacity: 0.9;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #2c3e50;
            font-size: 20px;
            margin-bottom: 15px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .kpi-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .kpi-label {
            color: #7f8c8d;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        
        .kpi-value {
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
        }
        
        .kpi-change {
            font-size: 12px;
            margin-top: 5px;
        }
        
        .kpi-change.positive {
            color: #2ecc71;
        }
        
        .kpi-change.negative {
            color: #e74c3c;
        }
        
        .chart-container {
            margin-top: 15px;
        }
        
        .chart-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chart-item:hover {
            background: #e9ecef;
            cursor: pointer;
        }
        
        .chart-name {
            font-weight: 500;
            color: #2c3e50;
        }
        
        .chart-date {
            color: #7f8c8d;
            font-size: 12px;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: #5568d3;
            transform: translateY(-1px);
        }
        
        .history-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #3498db;
        }
        
        .history-command {
            font-weight: 500;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .history-result {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .history-time {
            color: #95a5a6;
            font-size: 12px;
            margin-top: 5px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-success {
            background: #d4edda;
            color: #155724;
        }
        
        .status-error {
            background: #f8d7da;
            color: #721c24;
        }
        
        .summary-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        .summary-profile {
            font-weight: 500;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .summary-text {
            color: #7f8c8d;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 16px;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            transition: all 0.3s;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #95a5a6;
        }
        
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Analytics Hub</h1>
            <p>Unified Executive Intelligence Dashboard</p>
            <div style="margin-top: 10px; font-size: 14px;">
                Last updated: {{ timestamp }}
            </div>
        </div>
        
        <div class="dashboard-grid">
            <!-- KPI Section -->
            <div class="card">
                <h2>📈 Key Performance Indicators</h2>
                {% if kpis %}
                <div class="kpi-grid">
                    {% for kpi in kpis %}
                    <div class="kpi-item">
                        <div class="kpi-label">{{ kpi.label }}</div>
                        <div class="kpi-value">{{ kpi.value }}</div>
                        {% if kpi.change %}
                        <div class="kpi-change {{ 'positive' if kpi.change > 0 else 'negative' }}">
                            {{ '+' if kpi.change > 0 else '' }}{{ kpi.change }}%
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <p>No KPI data available</p>
                </div>
                {% endif %}
            </div>
            
            <!-- Charts Section -->
            <div class="card">
                <h2>📉 Recent Charts</h2>
                <div class="chart-container">
                    {% if charts %}
                    {% for chart in charts[:5] %}
                    <div class="chart-item" onclick="window.open('{{ chart.path }}', '_blank')">
                        <div>
                            <div class="chart-name">{{ chart.name }}</div>
                            <div class="chart-date">{{ chart.date }}</div>
                        </div>
                        <button class="btn">View</button>
                    </div>
                    {% endfor %}
                    {% else %}
                    <div class="empty-state">
                        <div class="empty-state-icon">📉</div>
                        <p>No charts available</p>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Voice Summaries Section -->
            <div class="card">
                <h2>🎙 Voice Summaries</h2>
                {% if voice_summaries %}
                {% for summary in voice_summaries[:5] %}
                <div class="summary-item">
                    <div class="summary-profile">{{ summary.profile }}</div>
                    <div class="summary-text">{{ summary.text[:150] }}...</div>
                </div>
                {% endfor %}
                {% else %}
                <div class="empty-state">
                    <div class="empty-state-icon">🎙</div>
                    <p>No voice summaries available</p>
                </div>
                {% endif %}
            </div>
            
            <!-- Orchestration History Section -->
            <div class="card">
                <h2>🎯 Recent Commands</h2>
                {% if history %}
                {% for item in history[:5] %}
                <div class="history-item">
                    <div class="history-command">{{ item.command }}</div>
                    <div class="history-result">
                        <span class="status-badge status-{{ item.status }}">{{ item.status }}</span>
                        {{ item.message }}
                    </div>
                    <div class="history-time">{{ item.timestamp }}</div>
                </div>
                {% endfor %}
                {% else %}
                <div class="empty-state">
                    <div class="empty-state-icon">🎯</div>
                    <p>No command history available</p>
                </div>
                {% endif %}
            </div>
        </div>
        
        <!-- Full Width Sections -->
        <div class="card" style="margin-bottom: 20px;">
            <h2>📊 System Overview</h2>
            <div class="kpi-grid">
                <div class="kpi-item">
                    <div class="kpi-label">Total Profiles</div>
                    <div class="kpi-value">{{ stats.profiles }}</div>
                </div>
                <div class="kpi-item">
                    <div class="kpi-label">Total Reports</div>
                    <div class="kpi-value">{{ stats.reports }}</div>
                </div>
                <div class="kpi-item">
                    <div class="kpi-label">Total Charts</div>
                    <div class="kpi-value">{{ stats.charts }}</div>
                </div>
                <div class="kpi-item">
                    <div class="kpi-label">Commands Executed</div>
                    <div class="kpi-value">{{ stats.commands }}</div>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">
            🔄 Refresh
        </button>
    </div>
</body>
</html>
"""


@dashboard_bp.route('/analytics')
def analytics_hub():
    """
    Analytics Hub - Unified executive analytics dashboard.
    
    Displays:
    - Latest KPIs from kpi_analyzer
    - Recent charts from Phase 2
    - Voice summaries
    - Orchestration history from Phase 4B
    """
    try:
        from profile_manager import list_profiles
        from orchestrator import get_orchestration_history
        import pandas as pd
        
        # Get KPIs
        kpis = []
        try:
            from kpi_analyzer import analyze_kpis
            
            # Create sample data for demo
            df = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                'Revenue': [100000, 120000, 115000, 135000, 142000],
                'Cost': [60000, 70000, 65000, 75000, 80000]
            })
            
            result = analyze_kpis(df)
            
            if result['status'] == 'success':
                metrics = result['metrics']
                
                # Extract key KPIs
                kpis = [
                    {
                        'label': 'Total Revenue',
                        'value': f"${metrics['summary']['total']:,.0f}",
                        'change': metrics['growth'].get('growth_rate', 0) * 100 if metrics['growth'].get('growth_rate') else None
                    },
                    {
                        'label': 'Avg Revenue',
                        'value': f"${metrics['summary']['mean']:,.0f}",
                        'change': None
                    },
                    {
                        'label': 'Profit Margin',
                        'value': f"{metrics['financial'].get('profit_margin', 0) * 100:.1f}%",
                        'change': None
                    },
                    {
                        'label': 'Growth Rate',
                        'value': f"{metrics['growth'].get('growth_rate', 0) * 100:.1f}%",
                        'change': None
                    }
                ]
        except Exception as e:
            print(f"KPI error: {e}")
        
        # Get recent charts
        charts = []
        try:
            charts_dir = "./reports/charts"
            if os.path.exists(charts_dir):
                for filename in os.listdir(charts_dir):
                    if filename.endswith('.png'):
                        filepath = os.path.join(charts_dir, filename)
                        stat = os.stat(filepath)
                        modified_time = datetime.fromtimestamp(stat.st_mtime)
                        
                        charts.append({
                            'name': filename.replace('_', ' ').replace('.png', '').title(),
                            'path': filepath,
                            'date': modified_time.strftime("%Y-%m-%d %H:%M")
                        })
                
                # Sort by date (newest first)
                charts.sort(key=lambda x: x['date'], reverse=True)
        except Exception as e:
            print(f"Charts error: {e}")
        
        # Get voice summaries
        voice_summaries = []
        try:
            profiles = list_profiles()
            
            for profile in profiles[:5]:
                voice_summaries.append({
                    'profile': profile['name'],
                    'text': f"Profile {profile['name']} has {profile['interaction_count']} interactions. Recent activity shows consistent engagement."
                })
        except Exception as e:
            print(f"Voice summaries error: {e}")
        
        # Get orchestration history
        history = []
        try:
            history_items = get_orchestration_history(limit=10)
            
            for item in history_items:
                history.append({
                    'command': item['command'],
                    'status': item['result']['status'],
                    'message': item['result']['message'],
                    'timestamp': item['timestamp']
                })
        except Exception as e:
            print(f"History error: {e}")
        
        # Get system stats
        stats = {
            'profiles': len(list_profiles()) if list_profiles() else 0,
            'reports': len(get_recent_reports()) if get_recent_reports() else 0,
            'charts': len(charts),
            'commands': len(history)
        }
        
        # Render template
        return render_template_string(
            ANALYTICS_TEMPLATE,
            kpis=kpis,
            charts=charts,
            voice_summaries=voice_summaries,
            history=history,
            stats=stats,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except Exception as e:
        return f"Analytics Hub error: {e}", 500


@dashboard_bp.route('/analytics/api')
def analytics_api():
    """
    Analytics Hub API - Returns analytics data as JSON.
    """
    try:
        from profile_manager import list_profiles
        from orchestrator import get_orchestration_history
        import pandas as pd
        
        # Get KPIs
        kpis = {}
        try:
            from kpi_analyzer import analyze_kpis
            
            df = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                'Revenue': [100000, 120000, 115000, 135000, 142000],
                'Cost': [60000, 70000, 65000, 75000, 80000]
            })
            
            result = analyze_kpis(df)
            
            if result['status'] == 'success':
                kpis = result['metrics']
        except Exception as e:
            kpis = {'error': str(e)}
        
        # Get charts count
        charts_count = 0
        try:
            charts_dir = "./reports/charts"
            if os.path.exists(charts_dir):
                charts_count = len([f for f in os.listdir(charts_dir) if f.endswith('.png')])
        except:
            pass
        
        # Get history
        history = []
        try:
            history = get_orchestration_history(limit=10)
        except:
            pass
        
        # Get profiles
        profiles = []
        try:
            profiles = list_profiles()
        except:
            pass
        
        return jsonify({
            'success': True,
            'data': {
                'kpis': kpis,
                'charts_count': charts_count,
                'history_count': len(history),
                'profiles_count': len(profiles),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
