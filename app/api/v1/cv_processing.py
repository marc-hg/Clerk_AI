import json
from io import StringIO

from app.services.file_info_extraction import extract_fields_user_v1
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Query
from typing import Dict, Any, List, Optional

from app.utils.pdf_conversion import file_to_text

router = APIRouter()


@router.post("/")
async def extract_cv_fields(
        file: UploadFile = File(None),
        cv_text: Optional[str] = Form(None),
) -> Dict[str, Any]:
    if not file and not cv_text:
        raise HTTPException(status_code=400, detail="Either file or text must be provided")

    try:
        if file and not cv_text:
            await validate_file(file)
            cv_text = await file_to_text(file)

        response = await extract_fields_user_v1(text=cv_text)

        if "error" in response:
            raise HTTPException(status_code=422, detail=response.get("error_message", "Unknown error occurred"))

        return {"status": "success", "data": response}

    except HTTPException:
        raise
    except json.JSONDecodeError as je:
        raise HTTPException(status_code=422, detail=f"Invalid JSON in response: {str(je)}")
    except (ValueError, IOError) as e:
        raise HTTPException(status_code=422, detail=f"Error processing input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


async def validate_file(file):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no filename")
    if not file.content_type or file.content_type.lower() != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
    if file.content_type.lower() not in ["application/pdf", "text/plain", "text/markdown"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF, text, or markdown file.")
