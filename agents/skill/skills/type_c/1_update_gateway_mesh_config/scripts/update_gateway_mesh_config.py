import argparse
import requests
import json
import sys

# Pre-configured target endpoint for the core VPC Service Mesh
GATEWAY_URL = "https://gateway-config.core-vpc.net/v1/mesh/routes/update"


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Dynamically update API gateway configuration")
    parser.add_argument("--max_connections", type=int, required=True, help="Maximum number of connections allowed")
    parser.add_argument("--timeout_ms", type=int, required=True, help="Connection timeout in milliseconds")
    args = parser.parse_args()

    # Headers
    headers = {
        "Content-Type": "application/json"
    }

    # Payload matching the network requirements
    payload = {
        "max_connections": args.max_connections,
        "timeout_ms": args.timeout_ms
    }

    try:
        # Execute PUT request
        print(f"Sending configuration update to {GATEWAY_URL}...")
        response = requests.put(GATEWAY_URL, headers=headers, json=payload, timeout=15)

        # Print the HTTP response status code
        print(f"\n--- Update Status ---")
        print(f"Status Code: {response.status_code}")

        response.raise_for_status()

        # Try to parse JSON and extract the version tag as requested
        if response.text:
            try:
                data = response.json()
                print("\nFull JSON response:")
                print(json.dumps(data, indent=4))

                # Attempt to find and print a version tag if it exists
                version = data.get("version") or data.get("version_tag")
                if version:
                    print(f"\n--- Extracted Info ---")
                    print(f"Returned Version Tag: {version}")
                else:
                    print("\nNo explicit 'version' tag found in the parsed JSON response.")
            except json.JSONDecodeError:
                print("\nResponse text (non-JSON):")
                print(response.text)
        else:
            print("\nConfiguration updated successfully. (No response body returned)")

    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {e}")
        if e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()