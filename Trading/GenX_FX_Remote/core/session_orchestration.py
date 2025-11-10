import json
import subprocess
import requests

def get_android_build_id():
    """Extracts the Android build fingerprint."""
    try:
        build_id = subprocess.check_output(['getprop', 'ro.build.fingerprint']).decode('utf-8').strip()
        return build_id
    except FileNotFoundError:
        # This will happen if 'getprop' is not available, e.g., not on an Android device
        return "not-an-android-device"
    except Exception as e:
        print(f"An error occurred while getting the build ID: {e}")
        return "error-getting-build-id"

def authenticate_device(config):
    """Sends an authentication request to the Jules session endpoint."""
    build_id = get_android_build_id()
    url = f"{config['jules_base_url']}/auth"
    headers = {"Content-Type": "application/json"}
    data = {
        "deviceid": build_id,
        "session_token": config["session_token"]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error authenticating device: {e}")
        return None

def trigger_flow(config, flow_name):
    """Triggers a specified orchestration flow."""
    build_id = get_android_build_id()
    url = f"{config['jules_base_url']}/trigger"
    headers = {
        "Authorization": f"Bearer {config['session_token']}",
        "Content-Type": "application/json"
    }
    data = {
        "flow": flow_name,
        "deviceid": build_id,
        "timestamp": "2023-10-27T10:00:00Z"  # Using a placeholder timestamp
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error triggering flow: {e}")
        return None

def sync_notes(config, notes_file):
    """Syncs notes or artifacts from a file to the LiteWriter endpoint."""
    build_id = get_android_build_id()
    url = config['litewriter_url']
    headers = {"Content-Type": "application/json"}
    try:
        with open(notes_file, 'r') as f:
            notes = json.load(f)

        data = {
            "deviceid": build_id,
            "notes": notes
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except FileNotFoundError:
        print(f"Error: Notes file not found at '{notes_file}'")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{notes_file}'")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error syncing notes: {e}")
        return None