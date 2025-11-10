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

def update_state(agent_id, new_state):
    """Updates the agent's state in the communication hub."""
    state_url = f"{API_BASE_URL}/state/{agent_id}"

    print(f"Updating state for agent {agent_id}...")
    print(f"  New state: {json.dumps(new_state, indent=2)}")

    try:
        response = requests.post(state_url, json=new_state)
        response.raise_for_status()

        print("State updated successfully!")
        print("Server response:")
        print(json.dumps(response.json(), indent=2))

    except requests.exceptions.RequestException as e:
        print(f"Error updating state: {e}")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON response from server. Response text: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update an agent's state in the communication hub.")
    parser.add_argument("state_json", help="The JSON string for the new state.")

    args = parser.parse_args()

    agent_id = get_agent_id()

    if agent_id:
        try:
            new_state = json.loads(args.state_json)
            update_state(agent_id, new_state)
        except json.JSONDecodeError:
            print("Error: Invalid JSON string provided for the state.")