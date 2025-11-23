from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException

# Base URL for MicroService1 (override via env, e.g., http://localhost:8080)
MS1_BASE_URL = os.getenv("MS1_BASE_URL", "http://localhost:8080")
TIMEOUT = float(os.getenv("MS1_TIMEOUT", "5.0"))


async def _request(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
):
    """Perform an HTTP request to MicroService1."""
    async with httpx.AsyncClient(
        base_url=MS1_BASE_URL,
        timeout=TIMEOUT,
        follow_redirects=True,
    ) as client:
        resp = await client.request(
            method,
            path,
            params=params,
            json=json,
            headers=headers,
        )
    _raise_for_error(resp)
    return resp


def _raise_for_error(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)


# User endpoints --------------------------------------------------------------
async def create_user(body: Dict[str, Any]):
    return await _request("POST", "/users", json=body)


async def login(body: Dict[str, Any]):
    """Login endpoint - POST /sessions"""
    return await _request("POST", "/sessions", json=body)


async def get_user(user_id: str, headers: Optional[Dict[str, str]] = None):
    return await _request("GET", f"/users/{user_id}", headers=headers)


async def update_user(user_id: str, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
    return await _request("PATCH", f"/users/{user_id}", json=body, headers=headers)


async def delete_user(user_id: str, headers: Optional[Dict[str, str]] = None):
    return await _request("DELETE", f"/users/{user_id}", headers=headers)


# Note: Status endpoints are not implemented in MS1, keeping for backward compatibility
# but they will return 404 from MS1
async def get_user_status(user_id: str, headers: Optional[Dict[str, str]] = None):
    return await _request("GET", f"/users/{user_id}/status", headers=headers)


async def update_user_status(user_id: str, status: Any, locked_until: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
    params = {"status": status}
    if locked_until is not None:
        params["locked_until"] = locked_until
    return await _request("PATCH", f"/users/{user_id}/status", params=params, headers=headers)
