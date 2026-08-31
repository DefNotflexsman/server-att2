import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_FILE = "database.db"
@app.route("/", methods=["GET", "HEAD"])
def index():
    return jsonify({
        "status": "online",
        "message": "Welcome to the API"
    }), 200
def init_db():
    """Creates the database tables if they do not already exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Example table schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            api_key TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # 1. Initialize DB at startup
    init_db()
    
    # 2. Run Flask server
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)