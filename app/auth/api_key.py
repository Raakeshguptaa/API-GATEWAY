import os
from dotenv import load_dotenv
load_dotenv()  # add this at the top

VALID_API_KEYS = {
    "abc123-service-key",
    "internal-microservice-key",
    "gateway-key",
}

# Loaded from environment, not hardcoded
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


def validate_api_key(api_key: str) -> bool:
    return api_key in VALID_API_KEYS


def validate_admin_key(key: str) -> bool:
    if not ADMIN_API_KEY:
        return False  # Fail safe: if env var is missing, deny all admin access
    return key == ADMIN_API_KEY