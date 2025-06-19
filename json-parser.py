import json
import re
from datetime import datetime

# Utility functions
def extract_ip(log_entry):
    # Attempt to find IP using regex
    ip_regex = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    match = re.search(ip_regex, json.dumps(log_entry))
    return match.group() if match else None

def normalize_timestamp(ts):
    try:
        return datetime.fromisoformat(ts).isoformat()
    except Exception:
        try:
            return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").isoformat()
        except Exception:
            return "Unknown"

def extract_username(log_entry):
    for key in ['user', 'username', 'userName', 'account', 'caller']:
        if key in log_entry:
            return log_entry[key]
    return "Unknown"

def extract_event_type(log_entry):
    for key in ['eventType', 'action', 'event_name', 'activity']:
        if key in log_entry:
            return log_entry[key]
    return "Unknown"

# Main function
def parse_logs(filename):
    with open(filename, 'r') as f:
        logs = json.load(f)

    parsed = []

    if isinstance(logs, dict) and 'records' in logs:
        entries = logs['records']
    elif isinstance(logs, list):
        entries = logs
    else:
        print("Unsupported JSON format.")
        return []

    for entry in entries:
        parsed.append({
            "timestamp": normalize_timestamp(entry.get('time', entry.get('timestamp', 'Unknown'))),
            "ip": extract_ip(entry),
            "username": extract_username(entry),
            "event_type": extract_event_type(entry)
        })

    return parsed

# Save parsed data
def save_to_json(parsed_data, output_file='parsed_logs.json'):
    with open(output_file, 'w') as f:
        json.dump(parsed_data, f, indent=2)
    print(f"Normalized data saved to {output_file}")

# Entry point
if __name__ == "__main__":
    parsed = parse_logs("AzureIPs.json")  # or your log file
    save_to_json(parsed)
