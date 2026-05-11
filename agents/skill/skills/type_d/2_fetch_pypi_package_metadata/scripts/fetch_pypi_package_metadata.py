import argparse
import requests
import json
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch package metadata from PyPI")
    parser.add_argument("--package", type=str, required=True, help="The name of the Python package (e.g., requests)")
    args = parser.parse_args()

    # Construct the official PyPI JSON API endpoint
    url = f"https://pypi.org/pypi/{args.package}/json"

    # Headers expecting JSON response
    headers = {
        "Accept": "application/json"
    }

    try:
        # Execute GET request to fetch the metadata
        print(f"Fetching metadata for package '{args.package}' from: {url}...\n")
        response = requests.get(url, headers=headers, timeout=15)

        # Print the HTTP response status code
        print(f"--- Fetch Status ---")
        print(f"Status Code: {response.status_code}\n")

        response.raise_for_status()

        # Parse the response as JSON
        data = response.json()

        print("--- Full Metadata (JSON) ---")
        # Print truncated JSON to avoid overwhelming the console if it's too large,
        # but keep it complete enough for agent parsing.
        print(json.dumps(data, indent=4)[:2000] + "\n... [JSON truncated for display] ...\n")

        # Explicitly extract the version string from the 'info' dictionary
        info = data.get("info", {})
        version = info.get("version")

        if version:
            print(f"--- Extracted Information ---")
            print(f"Package: {args.package}")
            print(f"Latest Version: {version}")
        else:
            print("\nNo 'version' found in the 'info' dictionary.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if e.response is not None:
            print(f"Response status code: {e.response.status_code}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Failed to parse the response as JSON. Raw text:")
        print(response.text)
        sys.exit(1)


if __name__ == "__main__":
    main()