#!/usr/bin/evn python

from molnframework.api import APIClient

if __name__ == "__main__":
    api_client = APIClient("127.0.0.1","8000")
    api_client.GetResource("sample")
