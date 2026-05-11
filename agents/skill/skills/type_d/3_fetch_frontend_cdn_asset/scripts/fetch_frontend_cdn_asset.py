import argparse
import requests
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Download and save static frontend assets from CDNs")
    parser.add_argument("--url", type=str, required=True, help="The CDN URL of the asset to download")
    parser.add_argument("--output", type=str, required=True,
                        help="The local filename to save the asset as (e.g., jquery.min.js)")
    args = parser.parse_args()

    try:
        # Execute GET request with stream=True for safe file downloading
        print(f"Downloading asset from: {args.url}...\n")
        response = requests.get(args.url, stream=True, timeout=15)

        # Print the HTTP response status code
        print(f"--- Download Status ---")
        print(f"Status Code: {response.status_code}\n")

        response.raise_for_status()

        # Save the binary content to the specified output file in chunks
        with open(args.output, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        # Print the required success message
        print(f"--- Success ---")
        print(f"Asset successfully downloaded and saved to: {args.output}")

    except requests.exceptions.RequestException as e:
        print(f"Network request failed: {e}")
        if e.response is not None:
            print(f"Response status code: {e.response.status_code}")
        sys.exit(1)
    except IOError as e:
        print(f"File system error occurred while saving: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()