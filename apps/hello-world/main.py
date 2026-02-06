import argparse
import requests


def fetch_example(url: str) -> None:
    """Fetch content from the specified URL."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes")
        print(f"\nFirst 500 characters of response:\n{response.text[:500]}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")


def main():
    parser = argparse.ArgumentParser(description="CLI to fetch content from websites")
    parser.add_argument(
        "--url",
        type=str,
        default="https://www.example.com",
        help="URL to fetch (default: https://www.example.com)"
    )
    
    args = parser.parse_args()
    fetch_example(args.url)


if __name__ == "__main__":
    main()
