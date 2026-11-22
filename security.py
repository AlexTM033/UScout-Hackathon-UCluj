import os
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from dotenv import load_dotenv

load_dotenv()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Local dictionary of valid keys (MODULE 1)
VALID_API_KEYS = {
    os.getenv("API_KEY", "super-secret-admin-key"): "admin_user",
    "test-key-123": "test_user"
}

def verify_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
        
    if api_key_header not in VALID_API_KEYS:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
        
    return VALID_API_KEYS[api_key_header]
