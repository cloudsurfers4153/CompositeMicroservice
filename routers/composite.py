import asyncio
from fastapi import APIRouter, HTTPException
from services import ms2, ms3

router = APIRouter()

def _json_or_none(resp):
    return resp.json() if resp.content else None


@router.get("/movie-details/{movie_id}")
async def composite_movie_details(movie_id: int):
    """
    Composite endpoint that aggregates movie data from multiple microservices.
    Uses parallel execution (asyncio.gather) to fetch data concurrently from MS2 and MS3.
    
    This demonstrates:
    - Parallel execution using asyncio.gather() for concurrent API calls
    - Aggregation of data from multiple atomic microservices
    """
    try:
        # Parallel execution: fetch movie details and reviews concurrently
        # This demonstrates threading/parallel execution requirement
        movie_task = ms2.get_movie(movie_id)
        people_task = ms2.get_movie_people(movie_id)
        reviews_task = ms3.list_reviews({"movie_id": movie_id, "page": 1, "page_size": 10})
        
        # Execute all three requests in parallel using asyncio.gather
        movie_resp, people_resp, reviews_resp = await asyncio.gather(
            movie_task,
            people_task,
            reviews_task,
            return_exceptions=True
        )
        
        # Handle movie response
        if isinstance(movie_resp, Exception):
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")
        
        movie_data = _json_or_none(movie_resp)
        if not movie_data:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")
        
        # Handle people response (cast/crew)
        people_data = []
        if not isinstance(people_resp, Exception):
            people_data = _json_or_none(people_resp) or []
        
        # Handle reviews response
        reviews_data = {"total": 0, "items": []}
        if not isinstance(reviews_resp, Exception):
            reviews_data = _json_or_none(reviews_resp) or reviews_data
        
        # Aggregate all data
        return {
            "movie": movie_data,
            "cast_and_crew": people_data,
            "reviews": reviews_data,
            "_links": {
                "self": f"/composite/movie-details/{movie_id}",
                "movie": f"/composite/movies/{movie_id}",
                "reviews": f"/composite/reviews?movie_id={movie_id}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error aggregating movie details: {str(e)}")
