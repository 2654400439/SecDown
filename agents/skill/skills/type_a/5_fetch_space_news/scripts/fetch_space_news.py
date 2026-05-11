import argparse
import requests
import json
import sys

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch latest spaceflight news by topic")
    parser.add_argument("--search", type=str, default="SpaceX", help="Topic to search for (e.g., SpaceX, NASA)")
    parser.add_argument("--limit", type=int, default=5, help="Number of articles to fetch")
    args = parser.parse_args()

    # API endpoint
    url = "https://api.spaceflightnewsapi.net/v4/articles/"

    # Query parameters
    params = {
        "search": args.search,
        "limit": args.limit
    }

    # Headers
    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        # Extract and print results
        print("Full JSON response:")
        print(json.dumps(data, indent=4))

        if "results" in data and len(data["results"]) > 0:
            print(f"\n--- Top {len(data['results'])} Recent Articles for '{args.search}' ---")
            for i, article in enumerate(data["results"], 1):
                title = article.get("title", "No Title")
                published_at = article.get("published_at", "Unknown Date")
                news_site = article.get("news_site", "Unknown Source")
                print(f"{i}. [{news_site}] {title} ({published_at})")
        else:
            print(f"\nNo articles found for the topic '{args.search}'.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()