from flask import Flask, render_template, jsonify
import sqlite3
import json
import os
import logging
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('logs.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/logs')
def get_logs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100')
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(logs)
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 50')
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(alerts)
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total logs count
        cursor.execute('SELECT COUNT(*) as log_count FROM logs')
        log_count = cursor.fetchone()['log_count']
        
        # Get alert counts by severity
        cursor.execute('''
        SELECT severity, COUNT(*) as count 
        FROM alerts 
        GROUP BY severity
        ''')
        severity_counts = {row['severity']: row['count'] for row in cursor.fetchall()}
        
        # Get unique IPs count
        cursor.execute('SELECT COUNT(DISTINCT ip) as unique_ips FROM logs')
        unique_ips = cursor.fetchone()['unique_ips']
        
        # Get unique users count
        cursor.execute('SELECT COUNT(DISTINCT username) as unique_users FROM logs')
        unique_users = cursor.fetchone()['unique_users']
        
        conn.close()
        
        return jsonify({
            'log_count': log_count,
            'severity_counts': severity_counts,
            'unique_ips': unique_ips,
            'unique_users': unique_users
        })
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({"error": str(e)}), 500

# Initialize the database if it doesn't exist
def init_db():
    if not os.path.exists('logs.db'):
        try:
            from log_analyser import setup_database
            conn, _ = setup_database()
            conn.close()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

if __name__ == '__main__':
    # Ensure the database exists
    init_db()
    
    # Check if we need to process logs
    if not os.path.exists('logs.db') or os.path.getsize('logs.db') < 100:
        try:
            logger.info("Processing logs for first-time setup...")
            from log_analyser import main as process_logs
            process_logs()
        except Exception as e:
            logger.error(f"Error in initial log processing: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
