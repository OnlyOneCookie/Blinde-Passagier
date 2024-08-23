import argparse
import requests
from src.api import SBBWrapper


def main():
    parser = argparse.ArgumentParser(description="SBB API Key")
    parser.add_argument("api_key", help="Your SBB API key")
    args = parser.parse_args()

    wrapper = SBBWrapper('https://journey-maps.api.sbb.ch', args.api_key)

    try:
        data = wrapper.get('transfer', client='webshop', clientVersion='latest', lang='en', fromStationID='8503000',
                           toStationID='8507000')
        print(data)
    except requests.exceptions.HTTPError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
