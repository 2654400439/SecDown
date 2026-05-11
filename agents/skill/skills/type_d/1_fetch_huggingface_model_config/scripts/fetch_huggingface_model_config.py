import argparse
import requests
import json
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch a model config file from HuggingFace")
    parser.add_argument("--url", type=str, required=True, help="The direct URL to the config.json file")
    args = parser.parse_args()

    # Headers expecting JSON response
    headers = {
        "Accept": "application/json"
    }

    try:
        # Execute GET request to fetch the config
        print(f"Fetching model configuration from: {args.url}...\n")
        response = requests.get(args.url, headers=headers, timeout=15)

        # Print the HTTP response status code
        print(f"--- Fetch Status ---")
        print(f"Status Code: {response.status_code}\n")

        response.raise_for_status()

        # Parse the response as JSON
        data = response.json()

        print("--- Full Configuration (JSON) ---")
        print(json.dumps(data, indent=4))

        # Explicitly extract the architecture if available
        architectures = data.get("architectures")
        if architectures and isinstance(architectures, list) and len(architectures) > 0:
            print("\n--- Extracted Metadata ---")
            print(f"Primary Architecture: {architectures[0]}")
        else:
            print("\nNo 'architectures' list found in the configuration.")

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