SELECT
    cv.name,
    cv.country,
    STRING_AGG(
            DISTINCT concat(skill.name, ': ', cv_skill.value),
            ', '
    ) as candidate_skills,
    STRING_AGG(
            DISTINCT company.name,
            ', '
    ) as candidate_companies,
    cv.comment,
    cv.email,
    cv.phone,
    cv.filename
FROM cv
         INNER JOIN cv_skill ON cv.id = cv_skill.cv_id
         INNER JOIN skill ON cv_skill.skill_id = skill.id
         INNER JOIN cv_company ON cv.id = cv_company.cv_id
         INNER JOIN company ON cv_company.company_id = company.id
    [[WHERE cv.id IN (
    SELECT cv_id
    FROM cv_skill
    JOIN skill ON cv_skill.skill_id = skill.id
    WHERE {{skills}}
    GROUP BY cv_id
    HAVING COUNT(DISTINCT skill.name) = (
        -- Count how many skills were selected in the filter
        SELECT COUNT(*)
        FROM skill
        WHERE {{skills}}
    )
)]]
[[AND cv.id IN (
    SELECT cv_id
    FROM cv_company
    JOIN company ON cv_company.company_id = company.id
    WHERE {{companies}}
    AND company.id IS NOT NULL
)]]
[[AND cv.country IN ({{countries}})]]
GROUP BY cv.id, cv.name, cv.email, cv.phone, cv.country;
