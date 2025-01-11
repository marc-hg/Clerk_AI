from typing import Dict, Any
import psycopg2


class DatabaseService:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="clerk_ai",
            user="postgres",
            password="secret",
            host="localhost",
            port="5432"
        )

    async def store_cv_data(self, cv_data: Dict[str, Any]) -> int:
        """Store CV data in the database and return the CV ID."""
        with self.conn.cursor() as cur:
            # Insert CV main data
            cur.execute("""
                INSERT INTO cv (name, email, phone, country, cv_text, comment, filename)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                cv_data["name"],
                cv_data["email"],
                cv_data["phone"],
                cv_data["country"],
                cv_data["cv_text"],
                cv_data["comment"],
                cv_data["filename"]
            ))
            cv_id = cur.fetchone()[0]

            # Insert and link skills with values
            for skill_name, skill_value in cv_data["skills"].items():
                # Insert skill if not exists
                cur.execute("""
                    INSERT INTO skill (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """, (skill_name,))
                result = cur.fetchone()
                if result is None:
                    cur.execute("SELECT id FROM skill WHERE name = %s", (skill_name,))
                    result = cur.fetchone()
                skill_id = result[0]

                # Link skill to CV with value
                cur.execute("""
                    INSERT INTO cv_skill (cv_id, skill_id, value)
                    VALUES (%s, %s, %s)
                """, (cv_id, skill_id, skill_value))

            # Insert and link companies
            for company_name in cv_data["companies"]:
                cur.execute("""
                    INSERT INTO company (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """, (company_name,))
                result = cur.fetchone()
                if result is None:
                    cur.execute("SELECT id FROM company WHERE name = %s", (company_name,))
                    result = cur.fetchone()
                company_id = result[0]

                cur.execute("""
                    INSERT INTO cv_company (cv_id, company_id)
                    VALUES (%s, %s)
                """, (cv_id, company_id))

            self.conn.commit()
            return cv_id 

    async def check_cv_exists(self, filename: str) -> bool:
        """Check if a CV with the given filename already exists."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM cv WHERE filename = %s", (filename,))
            result = cur.fetchone()
            return result is not None

    async def get_cv_info(self, filename: str) -> Dict[str, Any]:
        """Get basic info about an existing CV."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email, country, filename 
                FROM cv 
                WHERE filename = %s
            """, (filename,))
            result = cur.fetchone()
            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "email": result[2],
                    "country": result[3],
                    "filename": result[4]
                }
            return None 