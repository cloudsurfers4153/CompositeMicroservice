from fastapi import FastAPI
from routers import users, movies, reviews, composite

app = FastAPI(
    title="Composite Microservice",
    description="Delegates operations to MS1, MS2, and MS3.",
    version="1.0.0"
)

app.include_router(users.router, prefix="/composite")
app.include_router(movies.router, prefix="/composite")
app.include_router(reviews.router, prefix="/composite")
app.include_router(composite.router, prefix="/composite")

@app.get("/")
def root():
    return {
        "message": "Composite Microservice is running",
        "routes": [
            "/composite/users/{id}",
            "/composite/movies/{id}",
            "/composite/reviews",
            "/composite/movie-details/{id}"
        ]
    }
