class HttpTransport:
    def __init__(self, base_url, timeout=15, session=None):
        if session is None:
            import requests

            session = requests.Session()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session

    def get(self, path, params=None):
        response = self.session.get(
            f"{self.base_url}{path}",
            params=params or {},
            timeout=self.timeout,
        )
        return _decode_response(response)

    def post(self, path, body):
        response = self.session.post(
            f"{self.base_url}{path}",
            json=body,
            timeout=self.timeout,
        )
        return _decode_response(response)


def _decode_response(response):
    try:
        payload = response.json()
    except ValueError:
        response.raise_for_status()
        raise
    if response.status_code >= 400 and not isinstance(payload, dict):
        response.raise_for_status()
    return payload
