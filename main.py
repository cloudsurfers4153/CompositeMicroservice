from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, movies, reviews, composite

app = FastAPI(
    title="Composite Microservice",
    description="Delegates operations to MS1, MS2, and MS3.",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/composite")
app.include_router(movies.router, prefix="/composite")
app.include_router(reviews.router, prefix="/composite")
app.include_router(composite.router, prefix="/composite")

@app.get("/")
def root():
    return {
        "message": "Composite Microservice is running",
        "services": {
            "MS1": "Users Service",
            "MS2": "Movies & People Service",
            "MS3": "Reviews Service"
        },
        "routes": {
            "users": [
                "POST /composite/sessions (login)",
                "POST /composite/users (register)",
                "GET /composite/users/{id}",
                "PATCH /composite/users/{id}",
                "DELETE /composite/users/{id}"
            ],
            "movies": [
                "GET /composite/movies",
                "POST /composite/movies",
                "GET /composite/movies/{id}",
                "PUT /composite/movies/{id}",
                "DELETE /composite/movies/{id}",
                "GET /composite/movies/{id}/people"
            ],
            "reviews": [
                "GET /composite/reviews",
                "POST /composite/reviews",
                "GET /composite/reviews/{id}",
                "PUT /composite/reviews/{id}",
                "DELETE /composite/reviews/{id}",
                "GET /composite/health"
            ],
            "composite": [
                "GET /composite/movie-details/{id}"
            ]
        }
    }
