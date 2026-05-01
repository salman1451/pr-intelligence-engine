import os
import json
from app.models.schemas import ReviewState
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

SECURITY_PROMPT = """
You are a senior application security engineer.
Review these code chunks for real security vulnerabilities only.

PR Title: {pr_title}
Code Chunks:
{chunks}

Check for: hardcoded secrets, SQL injection, command injection, path traversal,
insecure deserialization (pickle/eval/yaml.load), open redirects, XSS vectors.

Output ONLY valid JSON:
{{
  "findings": [
    {{"severity":"critical|high|medium|low","category":"","description":"","line_numbers":[],"suggested_fix":""}}
  ],
  "severity_max": "critical|high|medium|low|none"
}}
"""

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _pick_higher_severity(current: str, candidate: str) -> str:
    severity_rank = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    if severity_rank.get(candidate, 0) > severity_rank.get(current, 0):
        return candidate
    return current


def security_node(state: ReviewState):
    llm = ChatGroq(
        model=model_name,
        temperature=0,
        api_key=api_key,
    )

    prompt = ChatPromptTemplate.from_template(SECURITY_PROMPT)
    chain = prompt | llm | StrOutputParser()

    findings = []
    highest_severity = "none"

    # Process in chunks of 5 to avoid token limits
    chunks = state.chunks
    for i in range(0, len(chunks), 5):
        chunk_group = chunks[i : i + 5]
        
        content = chain.invoke({
            "pr_title": state.title,
            "chunks": json.dumps(chunk_group, indent=2)
        })

        if content:
            try:
                clean_content = content.strip().replace("```json", "").replace("```", "")
                result = json.loads(clean_content)
                findings.extend(result.get("findings", []))
                highest_severity = _pick_higher_severity(highest_severity, result.get("severity_max", "none"))
            except:
                pass

    return {
        "security": findings,
        "severity": highest_severity,
    }
