from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException

# Base URL for MicroService3 (override via env, e.g., http://localhost:8000)
MS3_BASE_URL = os.getenv("MS3_BASE_URL", "http://localhost:8000")
TIMEOUT = float(os.getenv("MS3_TIMEOUT", "5.0"))


async def _request(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
):
    """Perform an HTTP request to MicroService3."""
    async with httpx.AsyncClient(
        base_url=MS3_BASE_URL,
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


# Review endpoints -------------------------------------------------------------
async def list_reviews(params: Dict[str, Any]):
    """List reviews with filtering and pagination."""
    return await _request("GET", "/reviews", params=params)


async def create_review(body: Dict[str, Any]):
    """Create a new review."""
    return await _request("POST", "/reviews", json=body)


async def get_review(review_id: int, headers: Optional[Dict[str, str]] = None):
    """Get a review by ID. Supports ETag via If-None-Match header."""
    return await _request("GET", f"/reviews/{review_id}", headers=headers)


async def update_review(review_id: int, body: Dict[str, Any]):
    """Update an existing review."""
    return await _request("PUT", f"/reviews/{review_id}", json=body)


async def delete_review(review_id: int):
    """Delete a review."""
    return await _request("DELETE", f"/reviews/{review_id}")


# Health check endpoint --------------------------------------------------------
async def health_check():
    """Health check endpoint."""
    return await _request("GET", "/health")
