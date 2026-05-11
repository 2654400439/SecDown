import argparse
import requests
import json
import os
import sys


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Search for job postings using JSearch on RapidAPI")
    parser.add_argument("--query", type=str, required=True, help="Job search query (e.g., 'developer jobs in chicago')")
    parser.add_argument("--page", type=str, default="1", help="Page number to fetch")
    parser.add_argument("--num_pages", type=str, default="1", help="Number of pages to fetch")
    parser.add_argument("--country", type=str, default="us", help="Country code for search")
    parser.add_argument("--date_posted", type=str, default="all",
                        help="Date posted filter (e.g., all, today, 3days, week, month)")
    args = parser.parse_args()

    # Read API key from environment variable
    rapidapi_key = os.environ.get("RAPIDAPI_API_KEY")
    if not rapidapi_key:
        print("Error: RAPIDAPI_API_KEY environment variable is not set.")
        print("Please ensure the environment variable is configured before running this skill.")
        sys.exit(1)

    # API endpoint
    url = "https://jsearch.p.rapidapi.com/search"

    # Query parameters
    params = {
        "query": args.query,
        "page": args.page,
        "num_pages": args.num_pages,
        "country": args.country,
        "date_posted": args.date_posted
    }

    # Headers with Custom Gateway Authentication
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        # Execute GET request
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()

        # Parse JSON result
        data = response.json()

        print(f"\n--- Job Search Results for: '{args.query}' ---")

        # Print the full raw JSON for agent parsing
        print("\nFull JSON response:")
        print(json.dumps(data, indent=4))

        # Explicitly extract and print basic job info if available
        if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
            print("\n--- Extracted Job Listings (Top 5) ---")
            for i, job in enumerate(data["data"][:5], 1):
                title = job.get("job_title", "Unknown Title")
                employer = job.get("employer_name", "Unknown Employer")
                location = f"{job.get('job_city', '')}, {job.get('job_state', '')}".strip(", ")
                print(f"{i}. {title}")
                print(f"   Employer: {employer}")
                print(f"   Location: {location if location else 'Not specified'}\n")
        else:
            print("\nNo jobs found matching your criteria.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()