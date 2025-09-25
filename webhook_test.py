import requests
import json
from datetime import datetime

# Load data from result.json
try:
    with open("result.json", "r") as f:
        api_data = json.load(f)
    print(f"Loaded {len(api_data)} API endpoints from result.json")
except FileNotFoundError:
    print("Error: result.json file not found!")
    exit(1)
except json.JSONDecodeError:
    print("Error: Invalid JSON in result.json file!")
    exit(1)

# Your n8n webhook URL
webhook_url = "https://n8n.ppmproclean.com.au/webhook/a1877d41-a4a5-47ce-95af-c5134863b1f1"

# Send the ServiceM8 API data as JSON
payload = {
    "servicem8_data": api_data,
    "timestamp": datetime.now().isoformat(),  # Add timestamp for tracking
    "total_endpoints": len(api_data)
}
 
print(f"Sending {len(api_data)} ServiceM8 API endpoints to webhook...")

try:
    response = requests.post(webhook_url, json=payload, timeout=30)
    
    if response.status_code == 200:
        print("✅ Data sent successfully!")
        print(f"Response: {response.text}")
    else:
        print(f"❌ Failed to send data. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out after 30 seconds")
except requests.exceptions.ConnectionError:
    print("❌ Connection error - check your internet connection and webhook URL")
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")