"""
Quick Start Server for Executive Intelligence System
Starts the Flask web server on http://127.0.0.1:5000
"""

from flask import Flask
from dashboard_gateway import dashboard_bp
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = 'executive-intelligence-secret-key-2025'

# Register dashboard blueprint
app.register_blueprint(dashboard_bp)

# Add root route
@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Executive Intelligence System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                background: rgba(255,255,255,0.1);
                padding: 50px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 48px; margin-bottom: 20px; }
            p { font-size: 20px; margin-bottom: 30px; }
            a {
                display: inline-block;
                background: white;
                color: #667eea;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
                margin: 10px;
                transition: transform 0.3s;
            }
            a:hover { transform: scale(1.05); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Executive Intelligence System</h1>
            <p>AI-Powered Business Intelligence Platform</p>
            <p>Status: <strong>✅ ONLINE</strong></p>
            <div>
                <a href="/dashboard">📊 Main Dashboard</a>
                <a href="/dashboard/analytics">📈 Analytics Hub</a>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎯 EXECUTIVE INTELLIGENCE SYSTEM")
    print("="*70)
    print("\n🚀 Starting server...")
    print("\n📍 Server will be available at:")
    print("   • http://127.0.0.1:5000")
    print("   • http://localhost:5000")
    print("\n📊 Available endpoints:")
    print("   • Home: http://127.0.0.1:5000/")
    print("   • Dashboard: http://127.0.0.1:5000/dashboard")
    print("   • Analytics: http://127.0.0.1:5000/dashboard/analytics")
    print("   • API: http://127.0.0.1:5000/dashboard/analytics/api")
    print("\n⚠️  Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    logger.info("Executive Intelligence System starting...")
    
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        logger.info("Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Server error: {e}")
