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

def receive_messages(agent_id):
    """Polls the communication hub for new messages."""
    messages_url = f"{API_BASE_URL}/messages/{agent_id}"

    print(f"Checking for messages for agent {agent_id}...")

    try:
        response = requests.get(messages_url)
        response.raise_for_status()

        messages = response.json()

        if not messages:
            print("No new messages.")
            return

        print(f"Received {len(messages)} message(s):")
        for msg in messages:
            print(json.dumps(msg, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"Error receiving messages: {e}")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON response from server. Response text: {response.text}")

if __name__ == "__main__":
    agent_id = get_agent_id()

    if agent_id:
        receive_messages(agent_id)