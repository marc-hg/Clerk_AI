from fastapi import FastAPI
from app.api.v1.cv_processing import router as cv_processing_router
from app.api.v1.smart_search import router as smart_search_router
import uvicorn

app = FastAPI()
app.include_router(cv_processing_router, prefix="/v1/cv_processing", tags=["cv_processing"])
app.include_router(smart_search_router, prefix="/v1/smart_search", tags=["smart_search"])

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
