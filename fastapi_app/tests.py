import requests
from time import time

REQUEST_00 = "http://localhost:8000/healthcheck"
REQUEST_01 = "http://localhost:8000/file_upload"


def test_request(r, verbose=False):
    start = time()
    resp = requests.get(r, )
    duration = time() - start
    print(resp.status_code, duration)
    print(resp.text) if verbose else None


if __name__ == '__main__':
    test_request(REQUEST_00)
    test_request(REQUEST_01)
