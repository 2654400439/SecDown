import argparse
import requests
import re
import sys

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch webpage HTML and extract title tag")
    parser.add_argument("--url", type=str, default="https://www.python.org/", help="The URL of the webpage to fetch (e.g., https://www.python.org/)")
    args = parser.parse_args()

    # Headers specifying expected content type
    headers = {
        "Accept": "text/html"
    }

    try:
        # Execute GET request
        response = requests.get(args.url, headers=headers, timeout=10)
        response.raise_for_status()

        # Get the raw HTML content
        html_content = response.text

        # Use regex to extract the content inside the <title> tag
        # re.IGNORECASE handles <TITLE> or <title>, re.DOTALL handles multiline titles if any
        match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)

        print(f"\n--- Webpage Title Extraction ---")
        print(f"Target URL: {args.url}")

        if match:
            # Clean up leading/trailing whitespaces or newlines
            title = match.group(1).strip()
            print(f"Extracted Title: {title}")
        else:
            print("Error: Could not find a <title> tag in the returned HTML.")

    except requests.exceptions.RequestException as e:
        print(f"Network request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()