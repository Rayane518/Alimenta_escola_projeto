
import os

import requests
import streamlit as st

from dotenv import load_dotenv


load_dotenv()


class ApiClient:

    def __init__(self, base_url=None, timeout=30):
        self.base_url = (
            base_url
            or os.getenv(
                "API_BASE_URL",
                "http://127.0.0.1:5000"
            )
        ).rstrip("/")

        self.timeout = timeout
        self.session = requests.Session()

    def get(self, path, **kwargs):
        return self.session.get(
            f"{self.base_url}/{path.lstrip('/')}",
            timeout=self.timeout,
            **kwargs
        )

    def post(self, path, **kwargs):
        return self.session.post(
            f"{self.base_url}/{path.lstrip('/')}",
            timeout=self.timeout,
            **kwargs
        )

    def put(self, path, **kwargs):
        return self.session.put(
            f"{self.base_url}/{path.lstrip('/')}",
            timeout=self.timeout,
            **kwargs
        )

    def patch(self, path, **kwargs):
        return self.session.patch(
            f"{self.base_url}/{path.lstrip('/')}",
            timeout=self.timeout,
            **kwargs
        )

    def close(self):
        self.session.close()


def get_api_client():
    if "api_client" not in st.session_state:
        st.session_state["api_client"] = ApiClient()

    return st.session_state["api_client"]
