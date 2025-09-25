# ServiceM8 API Token Extractor & Webhook Integration

This project automates the extraction of ServiceM8 API tokens and sends them to an n8n webhook for further processing.

## Files

- `main.py` - Main script that logs into ServiceM8, extracts API tokens and saves them to result.json
- `webhook_test.py` - Script that reads the extracted data and sends it to an n8n webhook
- `result.json` - Contains the extracted API endpoints, cookies, and auth tokens
- `.env` - Environment file for storing login credentials (not included in repo)

## Setup

1. Create a `.env` file with your ServiceM8 credentials:
```
EMAIL=your_servicem8_email@example.com
PASSWORD=your_servicem8_password
```

2. Install required dependencies:
```bash
pip install selenium requests python-dotenv
```

3. Make sure you have Chrome browser installed (required for Selenium)

## Usage

### Extract ServiceM8 API Tokens
```bash
python main.py
```
This will:
- Log into ServiceM8
- Navigate to the Dispatch Board
- Extract API tokens and cookies
- Save results to `result.json`

### Send Data to Webhook
```bash
python webhook_test.py
```
This will:
- Read data from `result.json`
- Send it to the configured n8n webhook
- Display success/error messages

## Configuration

Update the webhook URL in `webhook_test.py`:
```python
webhook_url = "https://your-n8n-instance.com/webhook/your-webhook-id"
```

## Security Notes

- Never commit the `.env` file to version control
- The `.gitignore` file is configured to exclude sensitive files
- Log files are also excluded from the repository

## Requirements

- Python 3.7+
- Chrome browser
- ChromeDriver (automatically managed by Selenium)
- ServiceM8 account credentials
