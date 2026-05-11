import argparse
import requests
import json
import os
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Perform an advanced news search using Tavily API")
    parser.add_argument("--query", type=str, required=True, help="The search query string")
    parser.add_argument("--topic", type=str, default="news", help="The topic category (e.g., news, general)")
    parser.add_argument("--days", type=int, default=7, help="Number of days back to search")
    parser.add_argument("--max_results", type=int, default=3, help="Maximum number of results to return")
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
        "query": args.query,
        "topic": args.topic,
        "days": args.days,
        "max_results": args.max_results
    }

    try:
        # Execute POST request
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        print(f"\n--- Top {args.max_results} News Articles for '{args.query}' (Past {args.days} days) ---")

        # Print the full raw JSON for agent parsing
        print("\nFull JSON response:")
        print(json.dumps(data, indent=4))

        # Explicitly print Titles and URLs as requested by the nl_goal
        if "results" in data and len(data["results"]) > 0:
            print("\n--- Extracted Titles and URLs ---")
            for i, result in enumerate(data["results"], 1):
                title = result.get("title", "No Title")
                link = result.get("url", "No URL")
                print(f"{i}. {title}")
                print(f"   URL: {link}")
        else:
            print("\nNo results found matching your criteria.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()