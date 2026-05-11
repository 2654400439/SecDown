import argparse
import requests
import json
import sys

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch academic paper details from OpenAlex API")
    parser.add_argument("--search", type=str, default="Attention Is All You Need", help="Paper title or keywords to search for")
    parser.add_argument("--per_page", type=int, default=1, help="Number of results to return")
    args = parser.parse_args()

    # API endpoint
    url = "https://api.openalex.org/works"

    # Query parameters mapping (OpenAlex uses 'per-page' instead of 'per_page')
    params = {
        "search": args.search,
        "per-page": args.per_page
    }

    # Headers
    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        # Extract and print results
        print("Full JSON response:")
        print(json.dumps(data, indent=4))

        if "results" in data and len(data["results"]) > 0:
            print(f"\n--- Top Result(s) for '{args.search}' ---")
            for i, work in enumerate(data["results"], 1):
                title = work.get("title", "Unknown Title")
                pub_year = work.get("publication_year", "Unknown Year")
                doi = work.get("doi", "No DOI")
                print(f"Result {i}:")
                print(f"  Title: {title}")
                print(f"  Year : {pub_year}")
                print(f"  DOI  : {doi}")
        else:
            print(f"\nNo papers found matching the search: '{args.search}'.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()