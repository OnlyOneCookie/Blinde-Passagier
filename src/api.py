import requests
from urllib.parse import urlencode


class SBBWrapper:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "accept": "application/json"
        }

    def _request(self, method, endpoint, params=None):
        url = f"{self.base_url}/v1/{endpoint}"
        if params:
            encoded_params = []
            for key, value in params.items():
                if isinstance(value, list):
                    for v in value:
                        encoded_params.append(f"{key}={requests.utils.quote(str(v))}")
                else:
                    encoded_params.append(f"{key}={requests.utils.quote(str(value))}")
            url += "?" + "&".join(encoded_params)

        print(f"Requesting URL: {url}")

        response = requests.request(method, url, headers=self.headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response content: {response.text}")
            raise

        return response.json()

    def get(self, endpoint, **params):
        return self._request("GET", endpoint, params)
