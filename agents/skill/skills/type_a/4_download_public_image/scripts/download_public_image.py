import argparse
import requests
import sys

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Download a public image and save it to the local disk")
    parser.add_argument("--url", type=str, default="https://cataas.com/cat", help="The URL of the image to download")
    parser.add_argument("--output", type=str, default="downloaded_image.jpg", help="The local filename to save the image as (e.g., cat_pic.jpg)")
    args = parser.parse_args()

    # Headers specifying expected content type
    headers = {
        "Accept": "image/jpeg"
    }

    try:
        # Execute GET request with stream=True for binary data
        response = requests.get(args.url, headers=headers, stream=True, timeout=15)
        response.raise_for_status()

        # Write binary content to file in chunks
        with open(args.output, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

        print(f"\n--- Download Successful ---")
        print(f"Source URL: {args.url}")
        print(f"Saved to: {args.output}")

    except requests.exceptions.RequestException as e:
        print(f"Network request failed: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"File system error occurred while saving: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()