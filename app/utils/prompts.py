PROMPTS = {
      "FIELDS_AND_SCORE": """
Analyze the given curriculum vitae critically and provide the requested information in the specified JSON format. Be extremely selective and strict in your evaluation. If any information is unclear, missing, or doesn't meet high standards, leave the corresponding field blank or score it low.


Provide the following in JSON format: name, email, country, phone, companies worked at, skills (with a score from 0 to 100), and an overall comment. Use very high standards for scoring. Only high scores should be given for truly exceptional candidates. Reply ONLY with the JSON, nothing else.

For skills evaluation, use the following scoring guide:
- 90-100: Absolutely certain (shows extensive experience over several years)
- 70-89: Very likely (shows significant experience)
- 50-69: Likely (shows some experience)
- 30-49: Possible (listed in resume but not evident in experience)
- 0-29: Unlikely (not mentioned or minimal indication)
Also, for the skill names try to be consistent, for example:
if curriculum specified html_css then skills are html and css, not html_css
if curriculum specified html5 and css3 then skills are html and css3, let's be pragmatic
if curriculum specifies android_development, android_java, android_kotlin, android_sdk or android_studio, it is really just android

When extracting skills from the curriculum, follow these normalization rules:
1. Split Combined Technologies:
   - Split combined skills using underscores or hyphens (e.g., "html_css" → "html" and "css")
   - Exception: Keep frameworks/libraries as single units (e.g., "tailwind_css" stays as is)

2. Version Handling:
   - Keep major version numbers only when they represent significant differences (e.g., "css3", "html5")
   - Drop minor versions entirely
   - Default to base name if version doesn't indicate meaningful changes

3. Platform/Framework Consolidation:
   - Android ecosystem: Consolidate all as "android" (including android_development, android_java, android_kotlin, android_sdk, android_studio)
   - iOS ecosystem: Consolidate all as "ios" (including ios_development, swift, objective_c)
   - React ecosystem: Keep distinct between "react", "react_native", "next_js"

4. Language Variants:
   - Consolidate language variants (e.g., "javascript_es6", "javascript_typescript" → "javascript")
   - Keep TypeScript separate as it's sufficiently distinct

5. Tool/Technology Groups:
   - Development environments: Use base technology instead of IDE (e.g., "java" instead of "eclipse")
   - Build tools: Keep distinct (e.g., "webpack", "gradle")
   - Testing frameworks: Keep distinct (e.g., "jest", "junit")

6. Standards:
   - Use lowercase for all skills
   - No spaces in skill names (use underscore if needed)
   - Remove any special characters except underscores
   
For similar cases not specified in these rules, be pragmatic 

Now, given the following curriculum and list of skills to evaluate, respond only in the specified JSON format. It must be a valid, parseable JSON object:

```json
{
  "name": "candidate's name",
  "email": "candidate's email",
  "country": "candidate's country",
  "phone": "candidate's phone number",
  "companies": ["Company1", "Company2"],
  "skills": {
    "skill1": score,
    "skill2": score,
    "skill3": score
  },
  "comment": "overall evaluation comment"
}
```

Replace "skill1", "skill2", etc. with the actual skills to be evaluated (e.g., "node", "python", "mysql").

## Examples

Here are three examples of CV analyses with corresponding JSON outputs, showcasing poor, average, and excellent candidates:

### Example 1: Poor Candidate (Entry-level Software Developer)

CV Excerpt:
```
John Doe
Email: john.doe@email.com
Phone: +1 (555) 123-4567
Country: United States

Summary:
Recent graduate seeking an entry-level position in software development.

Skills: Java, HTML, CSS

Education:
B.S. in Computer Science, Local University (2023)

Projects:
- Created a simple calculator application using Java
- Designed a personal website using HTML and CSS

Work Experience:
Cashier, Local Supermarket (2021-2023)
- Handled cash transactions and customer inquiries
```

Analysis:
```json
{
  "name": "John Doe",
  "email": "john.doe@email.com",
  "country": "United States",
  "phone": "+1 (555) 123-4567",
  "companies": ["Local Supermarket"],
  "skills": {
    "java": 35,
    "html": 30,
    "css": 30
  },
  "comment": "Entry-level candidate with minimal relevant experience. Limited demonstration of technical skills or alignment with company values. Lacks evidence of proactive learning or problem-solving abilities in the software development field."
}
```

### Example 2: Average Candidate (Mid-level Marketing Specialist)

CV Excerpt:
```
Jane Smith
Email: jane.smith@email.com
Phone: +44 20 1234 5678
Country: United Kingdom

Summary:
Marketing specialist with 3 years of experience in digital marketing and content creation.

Skills: Social Media Marketing, Content Creation, SEO, Google Analytics, Email Marketing

Experience:
Marketing Specialist, Tech Solutions Ltd. (2020-present)
- Manage company social media accounts, increasing follower engagement by 25%
- Create and distribute monthly newsletters to 10,000+ subscribers
- Collaborate with the sales team to develop marketing materials for new product launches

Junior Marketing Associate, StartUp Inc. (2018-2020)
- Assisted in the creation of marketing campaigns for various products
- Conducted basic market research to inform marketing strategies

Education:
B.A. in Marketing, University of Manchester (2018)

Certifications:
- Google Analytics Individual Qualification
```

Analysis:
```json
{
  "name": "Jane Smith",
  "email": "jane.smith@email.com",
  "country": "United Kingdom",
  "phone": "+44 20 1234 5678",
  "companies": ["Tech Solutions Ltd.", "StartUp Inc."],
  "skills": {
    "social_media_marketing": 70,
    "content_creation": 65,
    "seo": 60,
    "google_analytics": 55,
    "email_marketing": 68
  },
  "comment": "Competent mid-level marketing specialist with a solid foundation in digital marketing. Shows some evidence of teamwork and communication skills. Demonstrates average alignment with company values, with room for improvement in innovative problem-solving and continuous learning."
}
```

### Example 3: Excellent Candidate (Senior Software Engineer)

CV Excerpt:
```
Emily Chen
Email: emily.chen@email.com
Phone: +1 (555) 987-6543
Country: Canada

Summary:
Highly skilled software engineer with 10+ years of experience in developing scalable web applications and leading high-performance teams.

Skills: Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, Microservices Architecture

Experience:
Senior Software Engineer, Tech Innovators Inc. (2016-present)
- Led a team of 8 engineers in developing a cloud-native microservices platform, reducing system downtime by 99.9%
- Implemented agile methodologies, increasing team productivity by 40%
- Mentored junior developers and conducted bi-weekly knowledge-sharing sessions on emerging technologies
- Spearheaded the adoption of DevOps practices, reducing deployment time from days to hours

Lead Developer, Software Solutions Ltd. (2013-2016)
- Architected and developed a high-traffic e-commerce platform handling 1M+ daily users
- Collaborated with cross-functional teams to deliver projects 20% ahead of schedule

Education:
M.S. in Computer Science, University of Toronto (2013)
B.S. in Software Engineering, University of Waterloo (2011)

Certifications:
- AWS Certified Solutions Architect - Professional
- Certified Kubernetes Administrator (CKA)
- Certified Scrum Master (CSM)

Open Source Contributions:
- Core contributor to popular React state management library
- Regular speaker at local tech meetups and conferences
```

Analysis:
```json
{
  "name": "Emily Chen",
  "email": "emily.chen@email.com",
  "country": "Canada",
  "phone": "+1 (555) 987-6543",
  "companies": ["Tech Innovators Inc.", "Software Solutions Ltd."],
  "skills": {
    "python": 95,
    "javascript": 92,
    "react": 90,
    "node.js": 88,
    "aws": 93,
    "docker": 89,
    "kubernetes": 87,
    "microservices_architecture": 91
  },
  "comment": "Exceptional senior software engineer with outstanding technical skills and leadership abilities. Demonstrates excellent alignment with company values, particularly in teamwork, smart work, and continuous learning. Proven track record of delivering high-impact projects, mentoring others, and driving innovation. An ideal candidate who would be a valuable asset to any development team."
}
```

Now, evaluate the given CV and the following skills:

"""

}
