import os
from dotenv import load_dotenv
# Load environmental variables
load_dotenv()
# Constants
KIE_API_KEY = os.getenv('KIE_API_KEY', '')
DEFAULT_LANGUAGE = "german"
DEFAULT_DURATION = 8
DEFAULT_POLL_INTERVAL = 10
MAX_POLL_TIMEOUT = 900
