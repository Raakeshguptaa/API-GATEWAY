VALID_API_KEYS = {
    "abc123-service-key",
    "internal-microservice-key",
    "gateway-key"
}


def validate_api_key(api_key: str):
    if api_key in VALID_API_KEYS:
        return True
    return False