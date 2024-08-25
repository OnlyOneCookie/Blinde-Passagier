import argparse

import requests
from src.api import SBBWrapper
from src.utils import generate_instructions


def main():
    parser = argparse.ArgumentParser(description="SBB API Key")
    parser.add_argument("api_key", help="Your SBB API key")
    args = parser.parse_args()

    wrapper = SBBWrapper('https://journey-maps.api.sbb.ch', args.api_key)

    try:
        data = wrapper.get('transfer', client='webshop', clientVersion='latest', lang='en', fromStationID='8503000',
                           toStationID='8503000', fromTrack=15, toTrack=18, accessible='false')
        print(data)

        instructions = generate_instructions(data['features'])
        for instruction in instructions:
            print(instruction)

    except requests.exceptions.HTTPError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
