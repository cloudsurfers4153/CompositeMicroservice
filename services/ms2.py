from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException

# Base URL for MicroService2 (override via env, e.g., http://localhost:8000)
MS2_BASE_URL = os.getenv("MS2_BASE_URL", "http://localhost:8000")
TIMEOUT = float(os.getenv("MS2_TIMEOUT", "5.0"))


async def _request(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
):
    """Perform an HTTP request to MicroService2."""
    async with httpx.AsyncClient(
        base_url=MS2_BASE_URL,
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


# Movie endpoints -------------------------------------------------------------
async def list_movies(params: Dict[str, Any]):
    return await _request("GET", "/movies", params=params)


async def create_movie(body: Dict[str, Any]):
    return await _request("POST", "/movies", json=body)


async def get_movie(movie_id: int, headers: Optional[Dict[str, str]] = None):
    return await _request("GET", f"/movies/{movie_id}", headers=headers)


async def update_movie(movie_id: int, body: Dict[str, Any]):
    return await _request("PUT", f"/movies/{movie_id}", json=body)


async def delete_movie(movie_id: int):
    return await _request("DELETE", f"/movies/{movie_id}")


async def get_movie_people(movie_id: int):
    return await _request("GET", f"/movies/{movie_id}/people")


# People endpoints ------------------------------------------------------------
async def list_people(params: Dict[str, Any]):
    return await _request("GET", "/people", params=params)


async def create_person(body: Dict[str, Any]):
    return await _request("POST", "/people", json=body)


async def get_person(person_id: int):
    return await _request("GET", f"/people/{person_id}")


async def update_person(person_id: int, body: Dict[str, Any]):
    return await _request("PUT", f"/people/{person_id}", json=body)


async def delete_person(person_id: int):
    return await _request("DELETE", f"/people/{person_id}")


async def get_person_movies(person_id: int):
    return await _request("GET", f"/people/{person_id}/movies")
