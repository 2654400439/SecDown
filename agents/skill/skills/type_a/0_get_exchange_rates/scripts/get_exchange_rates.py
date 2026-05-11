import argparse
import requests
import json
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch exchange rates using Frankfurter API")
    parser.add_argument("--base", type=str, default="USD", help="Base currency (e.g., USD)")
    parser.add_argument("--target", type=str, default="CNY", help="Target currency (e.g., CNY)")
    args = parser.parse_args()

    # API endpoint
    url = "https://api.frankfurter.app/latest"

    # Query parameters
    params = {
        "from": args.base,
        "to": args.target
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        # Extract and print rates
        if "rates" in data and args.target in data["rates"]:
            rate = data["rates"][args.target]
            print("Full JSON response:")
            print(json.dumps(data, indent=4))
            print(f"\n{args.base} to {args.target} rate: {rate}")
        else:
            print(f"Error: Could not find rate for {args.target} in the response.")
            print(json.dumps(data, indent=4))

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()