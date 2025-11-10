import requests
import json
import os

# --- Configuration ---
# In a real application, these would come from a config file,
# environment variables, or command-line arguments.
# The user has 5 accounts, so this script would be run 5 times
# with different details.
AGENT_NAME = "Jules - Lengkundee01"
AGENT_EMAIL = "lengkundee01@gmail.com"
API_BASE_URL = "http://127.0.0.1:8080/communication"
AGENT_ID_FILE = "agent_id.json"

def register_agent():
    """
    Registers this agent instance with the communication hub.
    """
    registration_url = f"{API_BASE_URL}/register"

    payload = {
        "name": AGENT_NAME,
        "email": AGENT_EMAIL
        # The other Agent fields (id, status, last_seen) are handled by the server.
    }

    print(f"Attempting to register agent '{AGENT_NAME}' with email '{AGENT_EMAIL}'...")

    try:
        response = requests.post(registration_url, json=payload)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)

        agent_data = response.json()
        agent_id = agent_data.get("id")

        if not agent_id:
            print("Error: Registration response did not include an agent ID.")
            return

        print(f"Registration successful! Agent ID: {agent_id}")

        # Save the agent ID for future use
        with open(AGENT_ID_FILE, "w") as f:
            json.dump({"agent_id": agent_id}, f)
        print(f"Agent ID saved to {AGENT_ID_FILE}")

    except requests.exceptions.RequestException as e:
        print(f"Error registering agent: {e}")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON response from server. Response text: {response.text}")


if __name__ == "__main__":
    register_agent()