import json
from typing import List, Dict, Any
from app.services.db_service import DatabaseService

QUERY_PROMPT = """You are an SQL query generator for a CV search system. You will generate queries against a materialized view called cv_aggregated.

Here's the view definition:
{view_definition}

Your query should:
1. Always SELECT id, name, email, country, candidate_skills, candidate_companies
2. Use array containment operator (@>) for skill matching to ensure ALL skills are present
3. Use ILIKE for fuzzy text matching when needed
4. Order results by candidate_skills DESC for relevance
5. Limit results to 10 unless specified otherwise

Example queries (and make sure your queries are similar to these with the same structure):

1. Finding candidates with specific skills and country:
SELECT id, name, email, country, candidate_skills, candidate_companies
FROM cv_aggregated
WHERE skills @> ARRAY['c#', 'devops']::varchar[]
  AND country ILIKE '%spain%'
ORDER BY candidate_skills DESC
LIMIT 10;

2. Finding candidates who worked at specific companies:
SELECT id, name, email, country, candidate_skills, candidate_companies
FROM cv_aggregated
WHERE EXISTS (
    SELECT 1 FROM unnest(companies) company
    WHERE company ILIKE '%google%'
)
ORDER BY candidate_skills DESC
LIMIT 10;

Available Skills in database:
{skills}

Available Companies in database:
{companies}

User Question: {question}

Respond in JSON format:
{{
    "sql": "your SQL query here",
    "explanation": "brief explanation of the query logic"
}}
"""

class QueryGenerator:
    def __init__(self):
        self.db_service = DatabaseService()
        with open('database/materialized-view.sql', 'r') as file:
            self.view_definition = file.read()

    async def get_available_skills(self) -> List[str]:
        """Fetch all available skills from the database."""
        with self.db_service.conn.cursor() as cur:
            cur.execute("SELECT name FROM skill ORDER BY name")
            return [row[0] for row in cur.fetchall()]

    async def get_available_companies(self) -> List[str]:
        """Fetch all available companies from the database."""
        with self.db_service.conn.cursor() as cur:
            cur.execute("SELECT name FROM company ORDER BY name")
            return [row[0] for row in cur.fetchall()]

    async def generate_query(self, question: str) -> Dict[str, Any]:
        """Generate SQL query from natural language question."""
        skills = await self.get_available_skills()
        companies = await self.get_available_companies()
        
        prompt = QUERY_PROMPT.format(
            view_definition=self.view_definition,
            skills=", ".join(skills),
            companies=", ".join(companies),
            question=question
        )

        # Get response from OpenAI
        from app.services.file_info_extraction import get_gpt_response
        response = await get_gpt_response(prompt=prompt)

        try:
            query_data = json.loads(response)
            return query_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")

    async def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute the generated SQL query and return results."""
        with self.db_service.conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            results = []
            for row in cur.fetchall():
                results.append(dict(zip(columns, row)))
            return results

    async def smart_search(self, question: str) -> Dict[str, Any]:
        """Complete pipeline: generate query, execute it, and return results."""
        try:
            # Generate query
            query_data = await self.generate_query(question)
            
            # Execute query
            results = await self.execute_query(query_data["sql"])
            
            return {
                "status": "success",
                "explanation": query_data["explanation"],
                "sql": query_data["sql"],
                "results": results
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            } 