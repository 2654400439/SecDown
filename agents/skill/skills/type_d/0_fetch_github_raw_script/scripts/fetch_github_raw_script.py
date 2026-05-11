import argparse
import requests
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch a raw script file from a URL")
    parser.add_argument("--url", type=str, required=True, help="The direct URL to the raw script file")
    args = parser.parse_args()

    try:
        # Execute GET request to fetch the raw script
        print(f"Fetching script from: {args.url}...\n")
        response = requests.get(args.url, timeout=15)

        # Print the HTTP response status code
        print(f"--- Fetch Status ---")
        print(f"Status Code: {response.status_code}\n")

        response.raise_for_status()

        # Extract and print the first 100 characters of the content
        content = response.text
        preview = content[:100]

        print("--- Script Content Preview (First 100 chars) ---")
        print(preview)

        if len(content) > 100:
            print("...\n[Content truncated]")
        else:
            print("\n[End of file]")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if e.response is not None:
            print(f"Response status code: {e.response.status_code}")
        sys.exit(1)


if __name__ == "__main__":
    main()