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

### **Step 2: Train Your AI Agent (MANDATORY)**

This is the most important step. You must train the AI on your database schema before you can ask it questions.

In the same terminal, run the training script:

```bash
python train.py
```

- **Wait for this script to complete.** It may take a minute.
- A successful training will create a file named `vanna-chroma.sqlite3`. This file is the AI's "memory."

**VERY IMPORTANT:** You **MUST** run this script successfully before proceeding to Step 3. The application will not work without it.

### **Step 3: Launch the Application**

Once the AI is trained, you can start the web application:

```bash
python ad_ai_app.py
```

The terminal will show that a server is running. You can now open your web browser and go to **`http://127.0.0.1:5000`** to start chatting with your AI agent.

---

## Troubleshooting

**Error Message: "Error: The AI model has not been trained."**

If you see this message in the chat window, it means you either:
1.  Forgot to run `python train.py`.
2.  The `train.py` script did not complete successfully.

**To fix this:**
1. Stop the application by pressing `Ctrl + C` in the terminal.
2. Run `python train.py` again and make sure there are no errors.
3. Once training is complete, restart the application with `python ad_ai_app.py`.
