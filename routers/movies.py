from urllib.parse import urljoin

from fastapi import APIRouter, Request, Response
from services import ms2

router = APIRouter()

def _json_or_none(resp):
    return resp.json() if resp.content else None


def _rewrite_card_url(data):
    """Convert relative card_url from MS2 to absolute using MS2_BASE_URL."""
    if isinstance(data, dict):
        card_url = data.get("card_url")
        if card_url and card_url.startswith("/"):
            data = {**data, "card_url": urljoin(ms2.MS2_BASE_URL.rstrip("/") + "/", card_url.lstrip("/"))}
    return data


@router.get("/movies")
async def composite_list_movies(request: Request):
    # Proxy query params directly to MS2
    upstream = await ms2.list_movies(dict(request.query_params))
    return _json_or_none(upstream)


@router.post("/movies")
async def composite_create_movie(body: dict, response: Response):
    upstream = await ms2.create_movie(body)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.get("/movies/{movie_id}")
async def composite_get_movie(movie_id: int, request: Request, response: Response):
    headers = {}
    if_none_match = request.headers.get("if-none-match")
    if if_none_match:
        headers["if-none-match"] = if_none_match

    upstream = await ms2.get_movie(movie_id, headers=headers)

    if etag := upstream.headers.get("etag"):
        response.headers["ETag"] = etag

    response.status_code = upstream.status_code
    if upstream.status_code == 304:
        return None

    return _json_or_none(upstream)


@router.put("/movies/{movie_id}")
async def composite_update_movie(movie_id: int, body: dict, response: Response):
    upstream = await ms2.update_movie(movie_id, body)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.delete("/movies/{movie_id}")
async def composite_delete_movie(movie_id: int, response: Response):
    upstream = await ms2.delete_movie(movie_id)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.get("/movies/{movie_id}/people")
async def composite_movie_people(movie_id: int):
    upstream = await ms2.get_movie_people(movie_id)
    return _json_or_none(upstream)


# Share card job endpoints ----------------------------------------------------
@router.post("/movies/{movie_id}/generate-share-card", status_code=202)
async def composite_generate_share_card(movie_id: int, response: Response):
    upstream = await ms2.generate_share_card(movie_id)
    response.status_code = upstream.status_code
    data = _json_or_none(upstream)
    return _rewrite_card_url(data)


@router.get("/movies/{movie_id}/share-card-jobs/{job_id}")
async def composite_get_share_card_job_status(movie_id: int, job_id: str):
    upstream = await ms2.get_share_card_job_status(movie_id, job_id)
    data = _json_or_none(upstream)
    return _rewrite_card_url(data)


# People endpoints ------------------------------------------------------------
@router.get("/people")
async def composite_list_people(request: Request):
    upstream = await ms2.list_people(dict(request.query_params))
    return _json_or_none(upstream)


@router.post("/people")
async def composite_create_person(body: dict, response: Response):
    upstream = await ms2.create_person(body)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.get("/people/{person_id}")
async def composite_get_person(person_id: int, response: Response):
    upstream = await ms2.get_person(person_id)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.put("/people/{person_id}")
async def composite_update_person(person_id: int, body: dict, response: Response):
    upstream = await ms2.update_person(person_id, body)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.delete("/people/{person_id}")
async def composite_delete_person(person_id: int, response: Response):
    upstream = await ms2.delete_person(person_id)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.get("/people/{person_id}/movies")
async def composite_person_movies(person_id: int):
    upstream = await ms2.get_person_movies(person_id)
    return _json_or_none(upstream)
