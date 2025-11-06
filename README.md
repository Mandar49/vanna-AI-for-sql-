# AI-Powered Business Intelligence Agent

Welcome to your personal AI-Powered Business Intelligence (BI) Agent. This application allows you to ask complex questions about your business data in plain English and get intelligent, data-driven answers.

This guide will walk you through the simple steps to get the application running on your laptop.

## How it Works

This tool uses a powerful AI model (`gemma:7b`) that runs completely offline on your machine. It connects directly to your company's internal database to analyze live data and provide you with real-time insights. The "Two-Brain" architecture automatically understands whether you're asking for a simple fact or a complex strategic recommendation, giving you the best possible answer without any extra effort.

---

## Getting Started: A Step-by-Step Guide

Please follow these instructions carefully to set up and launch the application.

### **Step 1: Prerequisites (What you need)**

Before you begin, please make sure you have the following installed on your laptop:

1.  **Python:** This is the programming language the application is built on.
2.  **MySQL:** The database where your company data is stored.
3.  **Ollama with Gemma-7B:** You've already confirmed you have this set up, which is perfect.

### **Step 2: Database Connection**

The application needs to know how to connect to your database. All the settings are located in the `common.py` file.

The default settings are:
*   **Database Name:** `ad_ai_testdb`
*   **User:** `root`
*   **Password:** (no password)
*   **Host:** `localhost`

If your MySQL setup is different, simply open the `common.py` file in a text editor and update the `AppConfig` section with your correct database credentials.

### **Step 3: Install the Required Software**

This step is easy. I have created a file named `requirements.txt` that lists all the software libraries the application needs.

1.  Open your terminal (Command Prompt, PowerShell, or Terminal on Mac).
2.  Navigate to the project folder.
3.  Run the following command to install everything automatically:
    ```bash
    pip install -r requirements.txt
    ```

### **Step 4: Train Your AI Agent**

This is a crucial one-time step. We need to "teach" the AI about your specific database so it knows how to answer your questions accurately.

1.  In your terminal, make sure you are still in the project folder.
2.  Run the training script with this command:
    ```bash
    python3 train.py
    ```
3.  You will see some output in the terminal as the AI learns your database structure. This process is quick and creates a `vanna_chroma_db` folder in your project directory. This is your AI's "memory."

### **Step 5: Launch the Application**

You're all set! Now you can start the main application.

1.  In your terminal, run the following command:
    ```bash
    python3 ad_ai_app.py
    ```
2.  This will start the local web server. You will see a message in the terminal indicating that the server is running.
3.  Open your web browser (like Chrome, Firefox, or Safari) and go to this address:
    ```
    http://localhost:5000
    ```

You should now see the chat interface for your AI BI Agent. You can start asking it questions about your business data right away!
