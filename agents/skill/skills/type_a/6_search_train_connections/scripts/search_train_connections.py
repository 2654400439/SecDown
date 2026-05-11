import argparse
import requests
import json
import sys

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Search for public train connections in Switzerland")
    parser.add_argument("--origin", type=str, default="Zurich", help="Departure station/city (e.g., Zurich)")
    parser.add_argument("--destination", type=str, default="Geneva", help="Arrival station/city (e.g., Geneva)")
    parser.add_argument("--direct", type=int, choices=[0, 1], default=1, help="1 for direct connections only, 0 for all connections")
    args = parser.parse_args()

    # API endpoint
    url = "https://transport.opendata.ch/v1/connections"

    # Query parameters mapping to the API requirements
    params = {
        "from": args.origin,
        "to": args.destination,
        "direct": args.direct
    }

    # Headers
    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        # Extract and print results
        print("Full JSON response:")
        print(json.dumps(data, indent=4))

        # Print a brief, human-readable summary of the top results
        if "connections" in data and len(data["connections"]) > 0:
            print(f"\n--- Found {len(data['connections'])} connections from {args.origin} to {args.destination} ---")
            for i, conn in enumerate(data["connections"][:5], 1):  # Show up to 5 summaries
                dep_time = conn.get("from", {}).get("departure", "Unknown Time")
                arr_time = conn.get("to", {}).get("arrival", "Unknown Time")
                duration = conn.get("duration", "Unknown Duration")
                print(f"{i}. Departure: {dep_time} | Arrival: {arr_time} | Duration: {duration}")
        else:
            print(f"\nNo connections found from {args.origin} to {args.destination}.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()