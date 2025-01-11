import asyncio
import os
from app.services.db_service import DatabaseService
from app.utils.pdf_conversion import file_path_to_text
from app.services.file_info_extraction import extract_fields_user_v1
from fastapi import HTTPException

async def process_single_cv_to_db(file_path: str) -> dict:
    """Process a single CV file and store it in the database."""
    try:
        filename = os.path.basename(file_path)
        cv_directory = os.path.dirname(file_path)
        error_directory = os.path.join(os.path.dirname(cv_directory), "error_cvs")
        
        # Create error directory if it doesn't exist
        if not os.path.exists(error_directory):
            os.makedirs(error_directory)
        
        # Check if CV already exists by filename
        db_service = DatabaseService()
        existing_cv = await db_service.get_cv_info(filename)
        
        if existing_cv:
            return {
                "status": "skipped",
                "message": f"CV already exists: {filename}",
                "existing_data": existing_cv
            }

        # Only proceed with text extraction and processing if file doesn't exist
        cv_text = file_path_to_text(file_path)
        if not cv_text:
            return {"status": "error", "message": f"Failed to extract text from {filename}"}

        try:
            # Process the CV
            cv_json = await extract_fields_user_v1(cv_text)
            cv_json['filename'] = filename
            
            # Store in database
            cv_id = await db_service.store_cv_data(cv_json)
            
            return {
                "status": "success",
                "cv_id": cv_id,
                "name": cv_json.get("name", ""),
                "email": cv_json.get("email", ""),
                "filename": filename
            }
        except HTTPException as he:
            # Move file to error directory instead of deleting
            error_file_path = os.path.join(error_directory, filename)
            os.rename(file_path, error_file_path)
            return {
                "status": "error",
                "message": f"{str(he.detail)} - File moved to error_cvs",
                "file_moved": True
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}

async def process_cv_directory():
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cv_directory = os.path.join(project_root, "data", "cv_storage")

    print(f"Processing CVs from: {cv_directory}")
    
    if not os.path.exists(cv_directory):
        raise FileNotFoundError(f"Directory not found: {cv_directory}")

    results = []
    errors = []

    for filename in os.listdir(cv_directory):
        if filename.endswith('.pdf'):
            print(f"\nProcessing: {filename}")
            file_path = os.path.join(cv_directory, filename)
            result = await process_single_cv_to_db(file_path)
            
            if result["status"] == "success":
                results.append(result)
                print(f"✓ Successfully processed: {result['name']} ({result['email']})")
            else:
                errors.append({"file": filename, "error": result["message"]})
                print(f"✗ Error processing {filename}: {result['message']}")

    print(f"\n=== Processing Complete ===")
    print(f"Successfully processed: {len(results)} CVs")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"- {error['file']}: {error['error']}")

    return {
        "status": "success",
        "processed": len(results),
        "errors": errors if errors else None
    }

if __name__ == "__main__":
    asyncio.run(process_cv_directory()) 