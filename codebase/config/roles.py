"""
Role configurations for the interview platform.
Defines 7 professional roles with their attributes.
"""

# 8 Professional Roles
ROLES = [
    "Software Engineer",
    "Data Scientist",
    "Frontend Engineer",
    "DevOps Engineer",
    "Product Manager",
    "UX Designer",
    "Data Analyst",
    "Sales Representative",
]

# Role metadata
ROLE_INFO = {
    "Software Engineer": {
        "industry": "Technology",
        "focus_areas": ["System design", "Algorithms", "Debugging", "Architecture"],
        "skills": ["Coding", "Problem solving", "Design patterns", "Scalability"],
    },
    "Data Scientist": {
        "industry": "Technology",
        "focus_areas": ["ML", "Statistics", "Data analysis", "Model building"],
        "skills": ["Python", "R", "Statistics", "ML frameworks"],
    },
    "Frontend Engineer": {
        "industry": "Technology",
        "focus_areas": ["UI/UX", "Performance", "Frameworks", "Accessibility"],
        "skills": ["React/Vue", "JavaScript", "CSS", "Web optimization"],
    },
    "DevOps Engineer": {
        "industry": "Technology",
        "focus_areas": ["Infrastructure", "CI/CD", "Monitoring", "Automation"],
        "skills": ["Docker", "Kubernetes", "AWS/GCP", "Scripting"],
    },
    "Product Manager": {
        "industry": "Product",
        "focus_areas": ["Strategy", "User research", "Roadmapping", "Metrics"],
        "skills": ["Prioritization", "Communication", "Analysis", "Leadership"],
    },
    "UX Designer": {
        "industry": "Design",
        "focus_areas": ["User research", "Prototyping", "Testing", "Wireframing"],
        "skills": ["Figma", "User research", "Information architecture", "Usability"],
    },
    "Data Analyst": {
        "industry": "Business",
        "focus_areas": ["SQL", "Visualization", "Reporting", "Business intelligence"],
        "skills": ["SQL", "Excel", "Tableau", "Data storytelling"],
    },
    "Sales Representative": {
        "industry": "Sales",
        "focus_areas": ["Lead generation", "Relationship building", "Negotiation", "Closing deals"],
        "skills": ["Communication", "Persuasion", "CRM", "Target achievement"],
    },
}

# Interview types
INTERVIEW_TYPES = [
    "Technical Interview",
    "Behavioral Interview",
]

# User personas for testing
PERSONAS = ["Confused", "Efficient", "Chatty", "Edge-Case"]

PERSONA_DESCRIPTIONS = {
    "Confused": "Unsure, needs guidance and clarification",
    "Efficient": "Quick, direct, concise responses",
    "Chatty": "Long, detailed, sometimes off-topic stories",
    "Edge-Case": "Challenging inputs, tests system robustness",
}
