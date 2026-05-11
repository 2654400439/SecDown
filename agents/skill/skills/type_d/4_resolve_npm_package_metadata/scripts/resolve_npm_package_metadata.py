import argparse
import requests
import json
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch package metadata from the npm registry")
    parser.add_argument("--package", type=str, required=True, help="The name of the npm package (e.g., express)")
    args = parser.parse_args()

    # Construct the official npm registry endpoint
    url = f"https://registry.npmjs.org/{args.package}"

    # Headers expecting JSON response
    headers = {
        "Accept": "application/json"
    }

    try:
        # Execute GET request to fetch the metadata
        print(f"Fetching metadata for npm package '{args.package}' from: {url}...\n")
        response = requests.get(url, headers=headers, timeout=15)

        # Print the HTTP response status code
        print(f"--- Fetch Status ---")
        print(f"Status Code: {response.status_code}\n")

        response.raise_for_status()

        # Parse the response as JSON
        data = response.json()

        print("--- Full Metadata (JSON) ---")
        # Print truncated JSON to avoid overwhelming the console,
        # as npm metadata can be extremely large.
        print(json.dumps(data, indent=4)[:2000] + "\n... [JSON truncated for display] ...\n")

        # Explicitly extract the 'latest' version and its tarball URL
        dist_tags = data.get("dist-tags", {})
        latest_version = dist_tags.get("latest")

        if latest_version:
            # Navigate to the specific version data to find the distribution tarball
            version_data = data.get("versions", {}).get(latest_version, {})
            tarball_url = version_data.get("dist", {}).get("tarball")

            print(f"--- Extracted Information ---")
            print(f"Package: {args.package}")
            print(f"Latest Version: {latest_version}")
            print(f"Tarball URL: {tarball_url if tarball_url else 'Not found'}")
        else:
            print("\nCould not resolve the 'latest' version tag in the metadata.")

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