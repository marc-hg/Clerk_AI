from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.query_generator import QueryGenerator

router = APIRouter()

@router.get("/search")
async def smart_search(question: str) -> Dict[str, Any]:
    """Search for candidates using natural language query."""
    try:
        generator = QueryGenerator()
        results = await generator.smart_search(question)
        
        if results["status"] == "error":
            raise HTTPException(status_code=422, detail=results["message"])
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 