from fastapi import APIRouter, Request, Response
from services import ms2

router = APIRouter()

def _json_or_none(resp):
    return resp.json() if resp.content else None


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
