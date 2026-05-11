import argparse
import requests
import json
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch public issues from a GitHub repository")
    parser.add_argument("--owner", type=str, default="kubernetes", help="Repository owner (e.g., kubernetes)")
    parser.add_argument("--repo", type=str, default="kubernetes", help="Repository name (e.g., kubernetes)")
    parser.add_argument("--state", type=str, default="open", help="State of the issues (e.g., open, closed, all)")
    parser.add_argument("--per_page", type=int, default=3, help="Number of issues to fetch per page")
    args = parser.parse_args()

    # API endpoint
    url = f"https://api.github.com/repos/{args.owner}/{args.repo}/issues"

    # Query parameters
    params = {
        "state": args.state,
        "per_page": args.per_page
    }

    # Headers
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        # Extract and print results
        print("Full JSON response:")
        print(json.dumps(data, indent=4))

        print(f"\n--- Successfully fetched {len(data)} issues for {args.owner}/{args.repo} ---")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()