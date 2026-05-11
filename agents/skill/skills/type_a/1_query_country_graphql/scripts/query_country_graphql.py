import argparse
import requests
import json
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch country info using Countries GraphQL API")
    parser.add_argument("--code", type=str, default="BR", help="Country code (e.g., BR, US)")
    args = parser.parse_args()

    # API endpoint
    url = "https://countries.trevorblades.com/"

    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # GraphQL Query payload
    query = f"""
    query {{
      country(code: "{args.code.upper()}") {{
        name
        capital
        languages {{
          name
        }}
      }}
    }}
    """

    payload = {
        "query": query
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        # Extract and print results
        print("Full JSON response:")
        print(json.dumps(data, indent=4))

        if "data" in data and data["data"].get("country"):
            country_data = data["data"]["country"]
            print(f"\n--- Extracted Information for {args.code.upper()} ---")
            print(f"Country Name: {country_data.get('name')}")
            print(f"Capital City: {country_data.get('capital')}")
            languages = [lang.get("name") for lang in country_data.get("languages", [])]
            print(f"Spoken Languages: {', '.join(languages)}")
        else:
            print(f"\nError: Could not find data for country code '{args.code.upper()}' in the response.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()