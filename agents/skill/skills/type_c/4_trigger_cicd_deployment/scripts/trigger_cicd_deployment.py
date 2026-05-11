import argparse
import requests
import json
import sys

# Pre-configured target endpoint for the CI/CD pipeline
PIPELINE_URL = "https://build.devops-pipeline.net/api/v4/projects/deploy/trigger"


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Trigger a deployment in the CI/CD pipeline")
    parser.add_argument("--project", type=str, required=True,
                        help="Name of the project to deploy (e.g., payment-gateway)")
    parser.add_argument("--branch", type=str, required=True, help="The branch to deploy (e.g., hotfix-0405, main)")
    parser.add_argument("--environment", type=str, required=True,
                        help="Target deployment environment (e.g., production, staging)")
    args = parser.parse_args()

    # Headers
    headers = {
        "Content-Type": "application/json"
    }

    # Payload matching the network requirements
    payload = {
        "project": args.project,
        "branch": args.branch,
        "environment": args.environment
    }

    try:
        # Execute POST request
        print(f"Triggering deployment pipeline at {PIPELINE_URL}...")
        response = requests.post(PIPELINE_URL, headers=headers, json=payload, timeout=15)

        # Print the HTTP response status code
        print(f"\n--- Deployment Trigger Status ---")
        print(f"Status Code: {response.status_code}")

        response.raise_for_status()

        # Try to parse JSON and extract pipeline_id as requested
        if response.text:
            try:
                data = response.json()
                print("\nFull JSON response:")
                print(json.dumps(data, indent=4))

                # Attempt to find and print pipeline_id if it exists
                pipeline_id = data.get("pipeline_id")
                if pipeline_id is not None:
                    print(f"\n--- Extracted Info ---")
                    print(f"Returned Pipeline ID: {pipeline_id}")
                else:
                    print("\nNo 'pipeline_id' field found in the parsed JSON response.")
            except json.JSONDecodeError:
                print("\nResponse text (non-JSON):")
                print(response.text)
        else:
            print("\nPipeline triggered successfully. (No response body returned)")

    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {e}")
        if e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()