import requests
import json
import os
import argparse

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8080/communication"
AGENT_ID_FILE = "agent_id.json"

def get_agent_id():
    """Retrieves the agent ID from the local file."""
    if not os.path.exists(AGENT_ID_FILE):
        print(f"Error: Agent ID file not found at {AGENT_ID_FILE}. Please register the agent first.")
        return None

    with open(AGENT_ID_FILE, "r") as f:
        data = json.load(f)
        return data.get("agent_id")

def send_message(sender_id, recipient_id, event_type, payload):
    """Sends a message to the communication hub."""
    message_url = f"{API_BASE_URL}/messages"

    message = {
        "sender_id": sender_id,
        "recipient_id": recipient_id,
        "event_type": event_type,
        "payload": payload
    }

    print(f"Sending message from agent {sender_id}...")
    print(f"  Recipient: {recipient_id}")
    print(f"  Event: {event_type}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(message_url, json=message)
        response.raise_for_status()
        print("Message sent successfully!")

    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a message from an agent to the communication hub.")
    parser.add_argument("event_type", help="The type of the event (e.g., 'task_update', 'deployment_status').")
    parser.add_argument("payload_json", help="The JSON string for the message payload.")
    parser.add_argument("--recipient", default="broadcast", help="The recipient agent ID or 'broadcast'.")

    args = parser.parse_args()

    agent_id = get_agent_id()

    if agent_id:
        try:
            payload = json.loads(args.payload_json)
            send_message(agent_id, args.recipient, args.event_type, payload)
        except json.JSONDecodeError:
            print("Error: Invalid JSON string provided for the payload.")