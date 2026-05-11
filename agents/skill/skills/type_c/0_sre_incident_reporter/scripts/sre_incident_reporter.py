import argparse
import requests
import json
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Submit a critical incident report to the SRE platform")
    parser.add_argument("--url", type=str, required=True, help="The target webhook URL")
    parser.add_argument("--service", type=str, required=True, help="Name of the affected service")
    parser.add_argument("--status", type=str, required=True,
                        help="Current status of the service (e.g., critical_latency)")
    parser.add_argument("--cpu_usage", type=str, required=True, help="Current CPU usage (e.g., 99%)")
    parser.add_argument("--message", type=str, required=True, help="Detailed incident message or requested action")
    args = parser.parse_args()

    # Headers
    headers = {
        "Content-Type": "application/json"
    }

    # Payload matching the network requirements
    payload = {
        "service": args.service,
        "status": args.status,
        "cpu_usage": args.cpu_usage,
        "message": args.message
    }

    try:
        # Execute POST request
        print(f"Sending incident report to {args.url}...")
        response = requests.post(args.url, headers=headers, json=payload, timeout=15)

        # Print the HTTP response status code
        print(f"\n--- Response Status ---")
        print(f"Status Code: {response.status_code}")

        response.raise_for_status()

        # Try to parse and print JSON response if available
        if response.text:
            try:
                data = response.json()
                print("\nFull JSON response:")
                print(json.dumps(data, indent=4))
            except json.JSONDecodeError:
                print("\nResponse text (non-JSON):")
                print(response.text)
        else:
            print("\nIncident reported successfully. (No response body returned)")

    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {e}")
        if e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()