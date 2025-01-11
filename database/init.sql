-- Drop tables if they exist (for clean recreation)
DROP TABLE IF EXISTS cv_skill;
DROP TABLE IF EXISTS cv_company;
DROP TABLE IF EXISTS cv;
DROP TABLE IF EXISTS skill;
DROP TABLE IF EXISTS company;

-- Create CV table (main table)
CREATE TABLE cv (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) UNIQUE NOT NULL,
                    cv_text TEXT,
                    comment TEXT,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    phone VARCHAR(50),
                    country VARCHAR(100)
);

-- Create Skill table (simplified, no value)
CREATE TABLE skill (
                       id SERIAL PRIMARY KEY,
                       name VARCHAR(100) UNIQUE NOT NULL
);

-- Create Company table
CREATE TABLE company (
                         id SERIAL PRIMARY KEY,
                         name VARCHAR(255) UNIQUE NOT NULL
);

-- Create CV-Skill join table (with value)
CREATE TABLE cv_skill (
                          cv_id INTEGER REFERENCES cv(id) ON DELETE CASCADE,
                          skill_id INTEGER REFERENCES skill(id) ON DELETE CASCADE,
                          value INTEGER CHECK (value >= 0 AND value <= 100),
                          PRIMARY KEY (cv_id, skill_id)
);

-- Create CV-Company join table
CREATE TABLE cv_company (
                            cv_id INTEGER REFERENCES cv(id) ON DELETE CASCADE,
                            company_id INTEGER REFERENCES company(id) ON DELETE CASCADE,
                            PRIMARY KEY (cv_id, company_id)
);

-- Create indexes
CREATE INDEX idx_cv_email ON cv(email);
CREATE INDEX idx_cv_name ON cv(name);
CREATE INDEX idx_skill_name ON skill(name);
CREATE INDEX idx_company_name ON company(name);
CREATE INDEX idx_cv_skill_value ON cv_skill(cv_id, value);
CREATE INDEX idx_cv_company_cv_id ON cv_company(cv_id);