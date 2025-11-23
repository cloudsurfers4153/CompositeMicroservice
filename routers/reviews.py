from fastapi import APIRouter, Request, Response, HTTPException
from typing import Optional
from services import ms1, ms2, ms3

router = APIRouter()

def _json_or_none(resp):
    return resp.json() if resp.content else None


async def _validate_foreign_keys(movie_id: Optional[int], user_id: Optional[int]):
    """
    Validate foreign key constraints by checking if referenced entities exist.
    This demonstrates logical foreign key constraint validation in the composite service.
    
    - movie_id must exist in MS2 (Movies service)
    - user_id must exist in MS1 (Users service)
    """
    errors = []
    
    # Validate movie_id exists in MS2
    if movie_id is not None:
        try:
            movie_resp = await ms2.get_movie(movie_id)
            if movie_resp.status_code != 200:
                errors.append(f"Movie with id {movie_id} does not exist")
        except HTTPException as e:
            if e.status_code == 404:
                errors.append(f"Movie with id {movie_id} does not exist")
            else:
                errors.append(f"Error validating movie: {e.detail}")
        except Exception as e:
            errors.append(f"Error validating movie: {str(e)}")
    
    # Validate user_id exists in MS1
    if user_id is not None:
        try:
            # Note: MS1 uses string UUIDs, but reviews use int user_id
            # Convert to string for MS1 lookup
            user_resp = await ms1.get_user(str(user_id))
            if user_resp.status_code != 200:
                errors.append(f"User with id {user_id} does not exist")
        except HTTPException as e:
            if e.status_code == 404:
                errors.append(f"User with id {user_id} does not exist")
            else:
                errors.append(f"Error validating user: {e.detail}")
        except Exception as e:
            # If validation fails, add to errors
            errors.append(f"User with id {user_id} does not exist or validation failed")
    
    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Foreign key validation failed",
                "errors": errors
            }
        )


@router.get("/reviews")
async def composite_list_reviews(request: Request):
    """List reviews with filtering and pagination."""
    # Forward all query parameters to MS3
    upstream = await ms3.list_reviews(dict(request.query_params))
    return _json_or_none(upstream)


@router.post("/reviews")
async def composite_create_review(body: dict, response: Response):
    """
    Create a new review with foreign key constraint validation.
    
    This demonstrates logical foreign key constraint validation:
    - Validates movie_id exists in MS2 before creating review
    - Validates user_id exists in MS1 before creating review
    """
    movie_id = body.get("movie_id")
    user_id = body.get("user_id")
    
    # Validate foreign key constraints
    await _validate_foreign_keys(movie_id, user_id)
    
    # If validation passes, create the review
    upstream = await ms3.create_review(body)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.get("/reviews/{review_id}")
async def composite_get_review(review_id: int, request: Request, response: Response):
    """Get a review by ID. Supports ETag via If-None-Match header."""
    headers = {}
    if_none_match = request.headers.get("if-none-match")
    if if_none_match:
        headers["if-none-match"] = if_none_match

    upstream = await ms3.get_review(review_id, headers=headers)

    # Forward ETag header if present
    if "etag" in upstream.headers:
        response.headers["ETag"] = upstream.headers["etag"]

    response.status_code = upstream.status_code
    
    # Handle 304 Not Modified
    if upstream.status_code == 304:
        return None

    return _json_or_none(upstream)


@router.put("/reviews/{review_id}")
async def composite_update_review(review_id: int, body: dict, response: Response):
    """Update an existing review."""
    upstream = await ms3.update_review(review_id, body)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.delete("/reviews/{review_id}")
async def composite_delete_review(review_id: int, response: Response):
    """Delete a review."""
    upstream = await ms3.delete_review(review_id)
    response.status_code = upstream.status_code
    return _json_or_none(upstream)


@router.get("/health")
async def composite_health_check():
    """Health check endpoint."""
    upstream = await ms3.health_check()
    return _json_or_none(upstream)
