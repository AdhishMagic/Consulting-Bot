import requests
import json

BASE_URL = "https://simp-consulting-bot-production.up.railway.app"

def test_endpoint(name, endpoint, payload):
    print(f"--- Testing {name} ({endpoint}) ---")
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
        if response.status_code == 200:
            print("✅ SUCCESS")
        else:
            print("❌ FAILED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    print("\n")

# 1. Test Message Handler (/chat)
test_endpoint(
    "Message Handler", 
    "/chat", 
    {"message": "Hello from verification script", "user_id": "test_user"}
)

# 2. Test Trigger Handler (/trigger)
test_endpoint(
    "Trigger Handler", 
    "/trigger", 
    {"trigger": "test_trigger", "user_id": "test_user", "data": {"key": "value"}}
)

# 3. Test Context Handler (/context)
test_endpoint(
    "Context Handler", 
    "/context", 
    {
        "context_id": "test_context", 
        "user_id": "test_user", 
        "question": "What is your name?", 
        "answer": "My name is Bot"
    }
)

# 4. Test Failure Handler (/failure)
test_endpoint(
    "Failure Handler", 
    "/failure", 
    {"user_id": "test_user", "error": "Test Error", "context": "test_context"}
)
