# AI-Powered Business Intelligence Agent

Welcome to your personal AI-Powered Business Intelligence (BI) Agent. This application allows you to ask complex questions about your business data in plain English and get intelligent, data-driven answers.

This guide will walk you through the simple, three-step process to get the application running on your Windows machine.

---

## Quick Start Guide (Windows)

### **Step 1: Install the Required Software**

Open your terminal (Command Prompt or PowerShell), navigate to this project's folder, and run the following command to install all the necessary software:

```bash
pip install -r requirements.txt
```

### **Step 2: Train Your AI Agent**

Next, run the one-time training script to teach the AI about your database. In the same terminal, run:

```bash
python train.py
```

This will create a `vanna_chroma_db` folder in your project directory. This is the AI's "memory."

### **Step 3: Launch the Application**

Finally, start the web application with this command:

```bash
python ad_ai_app.py
```

The terminal will show that a server is running. You can now open your web browser and go to **`http://localhost:5000`** to start chatting with your AI agent.
