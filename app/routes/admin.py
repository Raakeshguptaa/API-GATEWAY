import yaml
import secrets
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])

ROUTES_FILE = Path("config/routes.yaml")

# In-memory API key store (swap for Redis/DB in production)
_api_keys: dict[str, str] = {}  # key → label

ADMIN_SECRET = "admin-secret-change-me"  # move to .env in production


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def verify_admin(x_admin_secret: Optional[str] = Header(None)):
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin secret")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class RouteConfig(BaseModel):
    path: str
    target: str
    method: str = "GET"
    auth_required: bool = False
    rate_limit: Optional[dict] = None
    # example rate_limit: {"requests": 10, "window_seconds": 60}


class ApiKeyCreate(BaseModel):
    label: str  # human-readable name e.g. "mobile-app", "data-pipeline"


class ApiKeyResponse(BaseModel):
    key: str
    label: str


# ---------------------------------------------------------------------------
# Route management
# ---------------------------------------------------------------------------

@router.get("/routes", dependencies=[Depends(verify_admin)])
def list_routes():
    """Return all routes currently loaded from routes.yaml."""
    if not ROUTES_FILE.exists():
        return {"routes": []}
    with open(ROUTES_FILE) as f:
        config = yaml.safe_load(f) or {}
    return {"routes": config.get("routes", [])}


@router.post("/routes", status_code=201, dependencies=[Depends(verify_admin)])
def add_route(route: RouteConfig):
    """Append a new route to routes.yaml."""
    config = _load_routes_file()
    routes = config.setdefault("routes", [])

    # Prevent duplicates on the same path+method
    for existing in routes:
        if existing["path"] == route.path and existing["method"] == route.method:
            raise HTTPException(
                status_code=409,
                detail=f"Route {route.method} {route.path} already exists. Delete it first.",
            )

    routes.append(route.model_dump(exclude_none=True))
    _save_routes_file(config)
    return {"message": "Route added", "route": route}


@router.delete("/routes", dependencies=[Depends(verify_admin)])
def delete_route(path: str, method: str = "GET"):
    """Remove a route by path + method."""
    config = _load_routes_file()
    routes = config.get("routes", [])
    updated = [r for r in routes if not (r["path"] == path and r["method"] == method)]

    if len(updated) == len(routes):
        raise HTTPException(status_code=404, detail="Route not found")

    config["routes"] = updated
    _save_routes_file(config)
    return {"message": f"Deleted {method} {path}"}


# ---------------------------------------------------------------------------
# API key management
# ---------------------------------------------------------------------------

@router.get("/keys", dependencies=[Depends(verify_admin)])
def list_keys():
    """List all active API keys (labels only, not the raw keys)."""
    return {"keys": [{"label": label, "key_preview": f"{k[:6]}..."} for k, label in _api_keys.items()]}


@router.post("/keys", response_model=ApiKeyResponse, status_code=201, dependencies=[Depends(verify_admin)])
def create_key(body: ApiKeyCreate):
    """Generate a new API key and store it."""
    new_key = secrets.token_urlsafe(32)
    _api_keys[new_key] = body.label
    return ApiKeyResponse(key=new_key, label=body.label)


@router.delete("/keys/{key}", dependencies=[Depends(verify_admin)])
def revoke_key(key: str):
    """Revoke an API key immediately."""
    if key not in _api_keys:
        raise HTTPException(status_code=404, detail="Key not found")
    label = _api_keys.pop(key)
    return {"message": f"Revoked key for '{label}'"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_routes_file() -> dict:
    if not ROUTES_FILE.exists():
        ROUTES_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {"routes": []}
    with open(ROUTES_FILE) as f:
        return yaml.safe_load(f) or {"routes": []}


def _save_routes_file(config: dict):
    with open(ROUTES_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)