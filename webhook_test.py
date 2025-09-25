import requests
import json
from datetime import datetime

# Load data from result.json with comprehensive error handling
try:
    with open("result.json", "r") as f:
        api_data = json.load(f)
    
    # Check if api_data is None or empty
    if api_data is None:
        print("Error: No data found in result.json - file contains null!")
        exit(1)
    
    if not api_data:
        print("Error: No data found in result.json - file is empty or contains empty list!")
        exit(1)
    
    # Check if api_data is a list (expected format)
    if not isinstance(api_data, list):
        print(f"Error: Expected list format in result.json, but got {type(api_data).__name__}")
        exit(1)
    
    print(f"✅ Loaded {len(api_data)} API endpoints from result.json")
    
except FileNotFoundError:
    print("❌ Error: result.json file not found!")
    print("   Make sure the ServiceM8 extraction script has run successfully first.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"❌ Error: Invalid JSON in result.json file: {e}")
    print("   The result.json file may be corrupted or incomplete.")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error loading result.json: {e}")
    exit(1)

# Your n8n webhook URL
webhook_url = "https://n8n.ppmproclean.com.au/webhook/a1877d41-a4a5-47ce-95af-c5134863b1f1"

# Send the ServiceM8 API data as JSON
payload = {
    "servicem8_data": api_data,
    "timestamp": datetime.now().isoformat(),  # Add timestamp for tracking
    "total_endpoints": len(api_data)
} 

print(f"📤 Sending {len(api_data)} ServiceM8 API endpoints to webhook...")
print(f"🔗 Webhook URL: {webhook_url}")

try:
    response = requests.post(webhook_url, json=payload, timeout=30)
    
    if response.status_code == 200:
        print("✅ Data sent successfully!")
        print(f"📋 Response: {response.text}")
    else:
        print(f"❌ Failed to send data. Status code: {response.status_code}")
        print(f"📋 Response: {response.text}")
        exit(1)  # Exit with error code when webhook fails
        
except requests.exceptions.Timeout:
    print("❌ Request timed out after 30 seconds")
    print("   The webhook endpoint may be slow to respond.")
    exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Connection error - check your internet connection and webhook URL")
    print("   Verify the webhook URL is correct and accessible.")
    exit(1)
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)

print("🎉 Webhook test completed successfully!")