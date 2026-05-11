import argparse
import requests
import json
import sys

# Pre-configured target endpoint for the building IoT gateway
IOT_GATEWAY_URL = "https://controller.building-iot.net/api/v1/hvac/zones/override"


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Send HVAC control commands to the facility IoT gateway")
    parser.add_argument("--zone", type=str, required=True, help="Target HVAC zone (e.g., server_room_A)")
    parser.add_argument("--command", type=str, required=True,
                        help="Action command to execute (e.g., emergency_cool, standard_cool, heat)")
    parser.add_argument("--target_temp", type=int, required=True, help="Target temperature in Celsius")
    args = parser.parse_args()

    # Headers
    headers = {
        "Content-Type": "application/json"
    }

    # Payload matching the network requirements
    payload = {
        "zone": args.zone,
        "command": args.command,
        "target_temp": args.target_temp
    }

    try:
        # Execute POST request
        print(f"Sending HVAC command to {IOT_GATEWAY_URL}...")
        response = requests.post(IOT_GATEWAY_URL, headers=headers, json=payload, timeout=15)

        # Print the HTTP response status code
        print(f"\n--- Command Status ---")
        print(f"Status Code: {response.status_code}")

        response.raise_for_status()

        # Try to parse JSON and extract device_state as requested
        if response.text:
            try:
                data = response.json()
                print("\nFull JSON response:")
                print(json.dumps(data, indent=4))

                # Attempt to find and print device_state if it exists
                device_state = data.get("device_state")
                if device_state is not None:
                    print(f"\n--- Extracted Info ---")
                    print(f"Returned Device State: {device_state}")
                else:
                    print("\nNo 'device_state' field found in the parsed JSON response.")
            except json.JSONDecodeError:
                print("\nResponse text (non-JSON):")
                print(response.text)
        else:
            print("\nHVAC command executed successfully. (No response body returned)")

    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {e}")
        if e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()