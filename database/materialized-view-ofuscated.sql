CREATE MATERIALIZED VIEW cv_aggregated AS
SELECT
    cv.id,
    'Candidate_' || substr(md5(random()::text), 1, 8) as name,
    cv.country,
    cv.comment,
    'user_' || substr(md5(random()::text), 1, 6) || '@example.com' as email,
    '+' || (floor(random() * 89999) + 10000)::text || (floor(random() * 8999999) + 1000000)::text as phone,
    cv.filename,
    ARRAY_AGG(DISTINCT skill.name) as skills,
    ARRAY_AGG(DISTINCT concat(skill.name, ': ', cv_skill.value)) as skills_with_values,
    ARRAY_AGG(DISTINCT company.name) as companies,
    STRING_AGG(DISTINCT concat(skill.name, ': ', cv_skill.value), ', ') as candidate_skills,
    STRING_AGG(DISTINCT company.name, ', ') as candidate_companies
FROM cv
         INNER JOIN cv_skill ON cv.id = cv_skill.cv_id
         INNER JOIN skill ON cv_skill.skill_id = skill.id
         INNER JOIN cv_company ON cv.id = cv_company.cv_id
         INNER JOIN company ON cv_company.company_id = company.id
GROUP BY cv.id, cv.country, cv.comment, cv.filename;