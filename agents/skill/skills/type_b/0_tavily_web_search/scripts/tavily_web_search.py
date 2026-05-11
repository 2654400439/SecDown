import argparse
import requests
import json
import os
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Perform a web search using Tavily API")
    parser.add_argument("--query", type=str, required=True, help="The search query string")
    args = parser.parse_args()

    # Read API key from environment variable
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("Error: TAVILY_API_KEY environment variable is not set.")
        print("Please ensure the environment variable is configured before running this skill.")
        sys.exit(1)

    # API endpoint
    url = "https://api.tavily.com/search"

    # Headers
    headers = {
        "Content-Type": "application/json"
    }

    # Payload matching the network requirements
    payload = {
        "api_key": api_key,
        "query": args.query
    }

    try:
        # Execute POST request
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        print(f"\n--- Search Results for: '{args.query}' ---")

        # Print the full raw JSON for agent parsing
        print("\nFull JSON response:")
        print(json.dumps(data, indent=4))

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        # Print response text if available for debugging auth issues
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()