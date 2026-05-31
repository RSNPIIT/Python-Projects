import ollama
import json

def analyze_resume(resume_text , user_goal):
    prompt = f"""
You are a senior software engineer and hiring manager.

Evaluate the resume based on the user's goal

User goal: {user_goal}

STRICT RULES:
- Extract only relevant skills for this goal
- Remove irrelevant tools [excel for backend , etc]
- Identify real gaps
- Generate rooadmaps only for missing fields
- Make output different based on goals

Return only JSON:
{{
    "skills" : [],
    "missing_skills" : [],
    "roadmap" : [],
    "interview_questions" : []
}}

Resume:
{resume_text}
"""
    try:
        response = ollama.chat(
            model = "qwen3:8b",
            options = {"temperature" : 0.3},
            messages = [
                {"role" : "system" , "content" : "You're a strict hiring manager."},
                {"role" : "user" , "content" : prompt}
            ]
        )
        content = response["message"]["content"].strip()

        start = content.find("{")
        end = content.rfind("}") + 1

        return json.loads(content[start : end])

    except Exception as e:
        return {
            "skills" : [],
            "missing_skills" : [],
            "roadmap" : [],
            "interview_questions" : [],
            "error": str(e)
        }