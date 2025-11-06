# AI-Powered Business Intelligence Agent (Simplified MVP)

Welcome to your personal AI-Powered Business Intelligence (BI) Agent. This application allows you to ask complex questions about your business data in plain English and get intelligent, data-driven answers.

This simplified version is designed to be extremely easy to set up and run on your local machine for demonstration purposes.

---

## Quick Start Guide (Windows)

Please follow these three simple steps to launch the application.

### **Step 1: Install the Required Software**

Open your terminal (Command Prompt or PowerShell) and navigate to this project's folder. Then, run the following command to install all the necessary software in one go:

```bash
pip install -r requirements.txt
```

### **Step 2: Train Your AI Agent**

Next, you need to train the AI on your specific database. This is a one-time step that creates a local "memory" for the AI.

In the same terminal, run this command:

```bash
python train.py
```

You will see some text output as the AI learns. This will create a `vanna_chroma_db` folder in your project directory.

### **Step 3: Launch the Application**

You're ready to go! Start the web application with this final command:

```bash
python ad_ai_app.py
```

The terminal will show that a server is running. You can now open your web browser and navigate to **`http://localhost:5000`** to start chatting with your AI agent.
