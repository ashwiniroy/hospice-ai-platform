from fastapi import FastAPI

from app.api.routes import health
from app.api.routes import hospices
from app.api.routes import analytics
from app.api.routes import ai


app = FastAPI(
    title="Hospice AI API",
    version="1.0.0"
)


app.include_router(health.router)
app.include_router(hospices.router)
app.include_router(analytics.router)
app.include_router(ai.router)


@app.get("/")
def root():
    return {
        "message": "Hospice AI API is running"
    }