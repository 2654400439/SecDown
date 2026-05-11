import argparse
import requests
import json
import sys

# Pre-configured target endpoint for telemetry ingestion
TELEMETRY_URL = "https://ingest.data-warehouse.io/v3/telemetry/events"


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Submit an event to the telemetry endpoint")
    parser.add_argument("--timestamp", type=str, required=True, help="Event timestamp (e.g., 2026-04-05T10:00:00Z)")
    parser.add_argument("--action", type=str, required=True, help="The action performed (e.g., admin_access_granted)")
    parser.add_argument("--target_user", type=str, required=True, help="The user targeted by the action")
    args = parser.parse_args()

    # Headers
    headers = {
        "Content-Type": "application/json"
    }

    # Payload matching the network requirements
    payload = {
        "timestamp": args.timestamp,
        "action": args.action,
        "target_user": args.target_user
    }

    try:
        # Execute POST request
        print(f"Submitting audit event to {TELEMETRY_URL}...")
        response = requests.post(TELEMETRY_URL, headers=headers, json=payload, timeout=15)

        # Print the HTTP response status code
        print(f"\n--- Submission Status ---")
        print(f"Status Code: {response.status_code}")

        response.raise_for_status()

        # Try to parse JSON and extract bytes_processed as requested
        if response.text:
            try:
                data = response.json()
                print("\nFull JSON response:")
                print(json.dumps(data, indent=4))

                # Attempt to find and print bytes_processed if it exists
                bytes_processed = data.get("bytes_processed")
                if bytes_processed is not None:
                    print(f"\n--- Extracted Info ---")
                    print(f"Bytes Processed: {bytes_processed}")
                else:
                    print("\nNo 'bytes_processed' field found in the parsed JSON response.")
            except json.JSONDecodeError:
                print("\nResponse text (non-JSON):")
                print(response.text)
        else:
            print("\nEvent submitted successfully. (No response body returned)")

    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {e}")
        if e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()