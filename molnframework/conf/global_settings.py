import os

HOST = os.environ.get('WEHA_APP_HOST')
PORT = os.environ.get('WEHA_APP_PORT')
SECRET_KEY = ''
INSTALLED_SERVICES = []
TIME_ZONE = 'Europe/Stockholm'
INTEVAL_TIME = 5
MAX_RETRY = 5
HEALTH_PATH = 'health/report/'
HEALTH_INTEVAL_TIME = 1
HEALTH_MAX_REPORT_ERROR = 10
IGNORE_API = False
MF_USERNAME = os.environ.get('WEHA_API_USERNAME')
MF_PASSWORD = os.environ.get('WEHA_API_PASSWORD')
MANAGER_ADDRESS = os.environ.get('WEHA_API_HOST')
MANAGER_PORT = os.environ.get('WEHA_API_PORT')