import tempfile
import os
from typing import Optional
from fastapi import UploadFile
import pymupdf


async def file_to_text(file: UploadFile) -> Optional[str]:
    content_type = file.content_type

    # Create a temporary file to store the uploaded content
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        if content_type == "application/pdf":
            # Process PDF file
            doc = pymupdf.open(temp_file_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            return full_text
        elif content_type in ["text/plain", "text/markdown"]:
            # Process text or markdown file
            with open(temp_file_path, 'r', encoding='utf-8') as text_file:
                return text_file.read()
        else:
            print(f"Unsupported file type: {content_type}")
            return None
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)
