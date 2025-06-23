import json
import sqlite3
import os
from collections import Counter
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import requests

# Database setup
def setup_database():
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    
    # Create logs table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        ip TEXT,
        username TEXT,
        event_type TEXT,
        processed_at TEXT
    )
    ''')
    
    # Create alerts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_type TEXT,
        description TEXT,
        severity TEXT,
        timestamp TEXT
    )
    ''')
    
    conn.commit()
    return conn, cursor

# Store logs in SQLite database
def store_logs(logs):
    conn, cursor = setup_database()
    
    for log in logs:
        cursor.execute('''
        INSERT INTO logs (timestamp, ip, username, event_type, processed_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            log['timestamp'],
            log['ip'],
            log['username'],
            log['event_type'],
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    print(f"Stored {len(logs)} logs in the database.")

# Load logs from file
def load_logs(filename='parsed_logs.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading logs: {e}")
        return []

# Anomaly detection functions
def detect_failed_logins(logs, threshold=3, time_window_hours=1):
    # Group logs by IP and username
    ip_failures = Counter()
    username_failures = Counter()
    alerts = []
    
    # Filter for login events
    login_events = [log for log in logs if 'login' in log['event_type'].lower() or 'auth' in log['event_type'].lower()]
    
    for log in login_events:
        # This is simplified - in a real system we'd check for failed status
        # For demo purposes, we'll just count all login attempts
        ip_failures[log['ip']] += 1
        username_failures[log['username']] += 1
    
    # Check for IPs exceeding threshold
    for ip, count in ip_failures.items():
        if count >= threshold:
            alert = {
                'alert_type': 'EXCESSIVE_LOGIN_ATTEMPTS',
                'description': f"Multiple login attempts ({count}) from IP: {ip}",
                'severity': 'HIGH',
                'timestamp': datetime.now().isoformat()
            }
            alerts.append(alert)
    
    # Check for usernames with excessive logins
    for username, count in username_failures.items():
        if count >= threshold:
            alert = {
                'alert_type': 'ACCOUNT_TARGETING',
                'description': f"Multiple login attempts ({count}) for user: {username}",
                'severity': 'MEDIUM',
                'timestamp': datetime.now().isoformat()
            }
            alerts.append(alert)
    
    return alerts

def detect_unusual_activity_hours(logs):
    alerts = []
    business_hours_start = 9  # 9 AM
    business_hours_end = 17   # 5 PM
    
    for log in logs:
        try:
            log_time = datetime.fromisoformat(log['timestamp'])
            hour = log_time.hour
            
            if hour < business_hours_start or hour > business_hours_end:
                alert = {
                    'alert_type': 'OFF_HOURS_ACTIVITY',
                    'description': f"Activity detected outside business hours from {log['username']} at {log['timestamp']}",
                    'severity': 'LOW',
                    'timestamp': datetime.now().isoformat()
                }
                alerts.append(alert)
        except Exception as e:
            print(f"Error processing timestamp: {e}")
    
    return alerts

# Main anomaly detection function
def detect_anomalies(logs):
    all_alerts = []
    
    # Run various detection algorithms
    failed_login_alerts = detect_failed_logins(logs)
    unusual_hours_alerts = detect_unusual_activity_hours(logs)
    
    all_alerts.extend(failed_login_alerts)
    all_alerts.extend(unusual_hours_alerts)
    
    # Store alerts in the database
    if all_alerts:
        conn, cursor = setup_database()
        for alert in all_alerts:
            cursor.execute('''
            INSERT INTO alerts (alert_type, description, severity, timestamp)
            VALUES (?, ?, ?, ?)
            ''', (
                alert['alert_type'],
                alert['description'],
                alert['severity'],
                alert['timestamp']
            ))
        conn.commit()
        conn.close()
    
    return all_alerts

# Alert notification functions
def send_email_alert(alert, recipient='tejasripacharu@gmail.com'):
    # This is a placeholder for actual email sending functionality
    print(f"ALERT EMAIL to {recipient}: {alert['alert_type']} - {alert['description']}")
    
    # Uncomment and configure for actual email sending
    """
    msg = EmailMessage()
    msg.set_content(f"Alert: {alert['description']}\nSeverity: {alert['severity']}")
    msg['Subject'] = f"Security Alert: {alert['alert_type']}"
    msg['From'] = "security@yourcompany.com"
    msg['To'] = recipient
    
    # Configure your SMTP server here
    s = smtplib.SMTP('smtp.yourcompany.com', 587)
    s.starttls()
    s.login('username', 'password')
    s.send_message(msg)
    s.quit()
    """

def send_slack_alert(alert, webhook_url=None):
    # This is a placeholder for actual Slack notification
    print(f"SLACK ALERT: {alert['alert_type']} - {alert['description']}")
    
    if webhook_url:
        payload = {
            "text": f"*SECURITY ALERT*\nType: {alert['alert_type']}\nDescription: {alert['description']}\nSeverity: {alert['severity']}"
        }
        try:
            requests.post(webhook_url, json=payload)
        except Exception as e:
            print(f"Error sending Slack alert: {e}")

def notify_alerts(alerts):
    for alert in alerts:
        # Choose notification method based on severity
        if alert['severity'] == 'HIGH':
            send_email_alert(alert)
            send_slack_alert(alert)
        elif alert['severity'] == 'MEDIUM':
            send_slack_alert(alert)
        else:
            # Just log low severity alerts
            print(f"Low severity alert: {alert['description']}")

# Main function
def main():
    # Parse logs if not already done
    if not os.path.exists('parsed_logs.json'):
        from json_parser import parse_logs, save_to_json
        parsed = parse_logs('AzureIPs.json')
        save_to_json(parsed)
    
    # Load parsed logs
    logs = load_logs()
    
    # Store logs in the database
    store_logs(logs)
    
    # Detect anomalies
    print("Analyzing logs for anomalies...")
    alerts = detect_anomalies(logs)
    
    # Notify about alerts
    if alerts:
        print(f"Detected {len(alerts)} anomalies!")
        notify_alerts(alerts)
    else:
        print("No anomalies detected.")

if __name__ == "__main__":
    main()