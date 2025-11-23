from fastapi import APIRouter, Request, Response
from typing import Optional
from services import ms1

router = APIRouter()

def _json_or_none(resp):
    return resp.json() if resp.content else None


def _extract_auth_headers(request: Request) -> dict:
    """Extract authorization header from request to forward to MS1."""
    headers = {}
    auth_header = request.headers.get("authorization")
    if auth_header:
        headers["authorization"] = auth_header
    return headers


@router.post("/sessions")
async def composite_login(body: dict, response: Response):
    """Login endpoint - POST /sessions"""
    upstream = await ms1.login(body)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.post("/users")
async def composite_create_user(body: dict, request: Request, response: Response):
    """Register a new user"""
    upstream = await ms1.create_user(body)
    response.status_code = upstream.status_code
    
    # Forward Location header if present
    if "location" in upstream.headers:
        response.headers["Location"] = upstream.headers["location"]
    
    return _json_or_none(upstream)


@router.get("/users/{user_id}")
async def composite_get_user(user_id: str, request: Request, response: Response):
    """Get user profile - requires authentication"""
    headers = _extract_auth_headers(request)
    upstream = await ms1.get_user(user_id, headers=headers)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.patch("/users/{user_id}")
async def composite_update_user(user_id: str, body: dict, request: Request, response: Response):
    """Update user profile - requires authentication"""
    headers = _extract_auth_headers(request)
    upstream = await ms1.update_user(user_id, body, headers=headers)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.delete("/users/{user_id}")
async def composite_delete_user(user_id: str, request: Request, response: Response):
    """Delete (soft delete) user - requires authentication"""
    headers = _extract_auth_headers(request)
    upstream = await ms1.delete_user(user_id, headers=headers)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


# Note: Status endpoints are not implemented in MS1, but kept for backward compatibility
@router.get("/users/{user_id}/status")
async def composite_get_user_status(user_id: str, request: Request, response: Response):
    """Get user status - not implemented in MS1, will return 404"""
    headers = _extract_auth_headers(request)
    upstream = await ms1.get_user_status(user_id, headers=headers)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.patch("/users/{user_id}/status")
async def composite_update_user_status(
    user_id: str, 
    status: str, 
    request: Request,
    response: Response,
    locked_until: Optional[str] = None
):
    """Update user status - not implemented in MS1, will return 404"""
    headers = _extract_auth_headers(request)
    upstream = await ms1.update_user_status(user_id, status, locked_until, headers=headers)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)
