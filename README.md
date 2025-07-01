# Cloud Log Aggregator

A comprehensive cloud log aggregation, analysis, and visualization solution for multi-cloud environments. This system collects logs from various cloud services, normalizes them into a consistent format, detects security anomalies, and provides real-time alerting and visualization through a modern web dashboard.

## Features

- **Log Collection**: Parse and normalize logs from multiple cloud providers (AWS CloudTrail, Azure Activity Logs)
- **Data Storage**: Store parsed logs in SQLite database for efficient querying and analysis
- **Anomaly Detection**: Identify suspicious patterns including:
  - Multiple failed login attempts
  - Activity outside business hours
  - Unusual access patterns
- **Real-time Alerting**: Notification system for security events via console, email, or Slack
- **Interactive Dashboard**: Modern web interface for log visualization and monitoring
- **Containerized Deployment**: Docker support for easy deployment
- **CI/CD Integration**: GitHub Actions workflow for automated builds

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (optional, for containerized deployment)
- Git

### Installation

#### Option 1: Direct Installation

1. Clone the repository:
   ```
   git clone https://github.com/TejasriPacharu/cloud-aggregator.git
   cd cloud-aggregator
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the log parser to process sample logs:
   ```
   python json-parser.py
   ```

4. Run the log analyzer to detect anomalies:
   ```
   python log-analyser.py
   ```

5. Start the web dashboard:
   ```
   python app.py
   ```

6. Access the dashboard at http://localhost:5000

#### Option 2: Docker Deployment

1. Clone the repository:
   ```
   git clone https://github.com/TejasriPacharu/cloud-aggregator.git
   cd cloud-aggregator
   ```

2. Build and start the container:
   ```
   docker-compose up -d
   ```

3. Access the dashboard at http://localhost:5000

## Usage

### Adding New Log Sources

To add a new log source:

1. Place your log file in JSON format in the project directory
2. Update the `parse_logs` function in `json-parser.py` if your log format differs significantly
3. Run the parser:
   ```
   python json-parser.py
   ```

### Customizing Alerting

1. Edit notification settings in the `notify_alerts` function in `log-analyser.py`
2. For email alerts, configure SMTP settings in the `send_email_alert` function
3. For Slack alerts, add your webhook URL to the `send_slack_alert` function

## Development

### Project Structure

```
cloud-aggregator/
├── app.py                  # Flask web application
├── log-analyser.py         # Anomaly detection and alerting
├── json-parser.py          # Log parsing and normalization
├── templates/              # Web dashboard HTML templates
│   └── index.html          # Main dashboard template
├── logs.db                 # SQLite database (created on first run)
├── parsed_logs.json        # Normalized log data
├── AzureIPs.json           # Sample log data
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
└── docker-compose.yml      # Docker Compose configuration
```

### CI/CD Pipeline

The project includes a GitHub Actions workflow for continuous integration:

1. Automated builds triggered on push to main branch
2. Docker image built and pushed to Docker Hub
3. Deployment ready for cloud hosting

## Deployment Options

### AWS EC2 (Free Tier)

1. Launch an EC2 instance
2. Install Docker and Docker Compose
3. Clone the repository
4. Run with `docker-compose up -d`

### Railway

1. Connect your GitHub repository to Railway
2. Configure environment variables if needed
3. Deploy automatically with every git push

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
