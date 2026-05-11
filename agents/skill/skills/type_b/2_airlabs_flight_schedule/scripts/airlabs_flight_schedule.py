import argparse
import requests
import json
import os
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch flight schedules using AirLabs API")
    parser.add_argument("--flight_iata", type=str, default="AA100", help="Flight IATA code (e.g., AA100, BA12)")
    args = parser.parse_args()

    # Read API key from environment variable
    api_key = os.environ.get("AIRLABS_API_KEY")
    if not api_key:
        print("Error: AIRLABS_API_KEY environment variable is not set.")
        print("Please ensure the environment variable is configured before running this skill.")
        sys.exit(1)

    # API endpoint
    url = "https://airlabs.co/api/v9/schedules"

    # Query parameters (Note: api_key is passed in URL query per requirements)
    params = {
        "flight_iata": args.flight_iata,
        "api_key": api_key
    }

    # Headers
    headers = {
        "Accept": "application/json"
    }

    try:
        # Execute GET request
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        print(f"\n--- Flight Schedule for {args.flight_iata} ---")

        # Print the full raw JSON for agent parsing
        print("\nFull JSON response:")
        print(json.dumps(data, indent=4))

        # Explicitly extract and print the requested details
        if "response" in data and isinstance(data["response"], list) and len(data["response"]) > 0:
            flight_data = data["response"][0]
            dep_terminal = flight_data.get("dep_terminal", "Not specified")
            dep_time = flight_data.get("dep_time", "Not specified")

            print(f"\n--- Extracted Information ---")
            print(f"Departure Terminal: {dep_terminal}")
            print(f"Scheduled Departure Time: {dep_time}")
        else:
            print(f"\nNo schedule details found for flight {args.flight_iata}.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()