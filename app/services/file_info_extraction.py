import json
import re
from typing import Dict, Any, List
from fastapi import UploadFile, HTTPException
from openai import OpenAI

from app.config import OPENAI_API_KEY
from app.utils.pdf_conversion import file_to_text
from app.utils.prompts import PROMPTS

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


async def get_gpt_response(prompt: str, text: str = "") -> str:
    try:
        # Prepare the messages for the chat completion
        messages = [
            {"role": "system", "content": prompt}
        ]
        
        # Only add user message if text is provided
        if text:
            messages.append({"role": "user", "content": text})

        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000
        )

        content = response.choices[0].message.content
        content = re.sub(r'^```json\s*\n', '', content)
        content = re.sub(r'\n```\s*$', '', content)
        return content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in GPT response: {str(e)}")


async def extract_fields_user_v1(text: str) -> Dict[str, Any]:
    prompt = PROMPTS["FIELDS_AND_SCORE"]
    response = await get_gpt_response(prompt, text)

    result = {
        "name": "",
        "email": "",
        "country": "",
        "phone": "",
        "companies": [],
        "skills": {},
        "comment": "",
        "response": response,
        "cv_text": text,
    }

    try:
        response_dict = json.loads(response)
        result["name"] = response_dict.get("name", "")
        result["email"] = response_dict.get("email", "")
        result["country"] = response_dict.get("country", "")
        result["phone"] = response_dict.get("phone", "")
        result["companies"] = response_dict.get("companies", [])
        result["skills"] = response_dict.get("skills", {})
        if "comment" in response_dict:
            result["comment"] = response_dict["comment"]
        print(response_dict)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"Invalid JSON response: {str(e)}")

    # Validate required fields
    required_fields = ["name", "email", "country", "skills"]
    missing_fields = [field for field in required_fields if not result[field]]
    if missing_fields:
        raise HTTPException(status_code=422, detail=f"Missing required fields: {', '.join(missing_fields)}")

    return result
