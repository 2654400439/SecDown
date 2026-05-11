import argparse
import requests
import json
import os
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch commit history from a private GitHub repository")
    parser.add_argument("--owner", type=str, required=True, help="Repository owner (e.g., example-org)")
    parser.add_argument("--repo", type=str, required=True, help="Repository name (e.g., private-research-artifact)")
    parser.add_argument("--per_page", type=int, default=3, help="Number of latest commits to retrieve")
    args = parser.parse_args()

    # Read API token from environment variable
    github_pat = os.environ.get("GITHUB_PAT")
    if not github_pat:
        print("Error: GITHUB_PAT environment variable is not set.")
        print("Please ensure the environment variable is configured before running this skill.")
        sys.exit(1)

    # API endpoint
    url = f"https://api.github.com/repos/{args.owner}/{args.repo}/commits"

    # Query parameters
    params = {
        "per_page": args.per_page
    }

    # Headers with Bearer Token Authentication
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {github_pat}"
    }

    try:
        # Execute GET request
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        print(f"\n--- Latest {args.per_page} Commits for {args.owner}/{args.repo} ---")

        # Print the full raw JSON for agent parsing
        print("\nFull JSON response:")
        print(json.dumps(data, indent=4))

        # Explicitly extract and print Author and Message
        if isinstance(data, list) and len(data) > 0:
            print("\n--- Extracted Commit Details ---")
            for i, commit_data in enumerate(data, 1):
                commit_info = commit_data.get("commit", {})
                author = commit_info.get("author", {}).get("name", "Unknown Author")
                message = commit_info.get("message", "No Message").strip()

                # Truncate message if it's too long for a clean display
                short_message = message.split('\n')[0]

                print(f"{i}. Author: {author}")
                print(f"   Message: {short_message}\n")
        else:
            print("\nNo commits found for this repository.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()
