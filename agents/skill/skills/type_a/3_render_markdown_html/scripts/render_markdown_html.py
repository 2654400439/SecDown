import argparse
import requests
import sys

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Convert Markdown text to HTML using GitHub API")
    parser.add_argument("--text", type=str, required=True, help="The Markdown text to convert (e.g., 'Hello **world**!')")
    args = parser.parse_args()

    # API endpoint
    url = "https://api.github.com/markdown"

    # Headers for HTML response
    headers = {
        "Accept": "application/vnd.github.v3+html",
        "Content-Type": "application/json"
    }

    # Payload matching the network requirements
    payload = {
        "text": args.text
    }

    try:
        # Execute POST request
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()

        # Extract and print the rendered HTML
        print(f"\n--- Rendered HTML Output for input: '{args.text}' ---")
        # GitHub API returns raw HTML string when Accept header is set to html
        print(response.text.strip())

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()