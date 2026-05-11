import argparse
import requests
import json
import sys

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch current weather data using Open-Meteo API")
    parser.add_argument("--latitude", type=float, default=35.6895, help="Latitude of the location (e.g., 35.6895)")
    parser.add_argument("--longitude", type=float, default=139.6917, help="Longitude of the location (e.g., 139.6917)")
    args = parser.parse_args()

    # API endpoint
    url = "https://api.open-meteo.com/v1/forecast"

    # Query parameters
    params = {
        "latitude": args.latitude,
        "longitude": args.longitude,
        "current_weather": "true"
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

        if "current_weather" in data:
            weather = data["current_weather"]
            print(f"\n--- Current Weather at {args.latitude}, {args.longitude} ---")
            print(f"Temperature: {weather.get('temperature')} °C")
            print(f"Wind Speed: {weather.get('windspeed')} km/h")
            print(f"Time: {weather.get('time')}")
        else:
            print("\nError: Could not find current_weather data in the response.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()