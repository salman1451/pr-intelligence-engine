import os
import json
from app.models.schemas import ReviewState
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

STYLE_PROMPT = """
You are a senior software engineer enforcing coding standards.
Review the changed code and find style and convention violations.

Code Chunks:
{chunks}

Check for: naming conventions, missing docstrings, improper error handling patterns,
import ordering, overly long functions (>50 lines), missing type hints.

Output ONLY valid JSON:
{{
  "findings": [
    {{"rule":"","line_numbers":[],"description":"","suggested_correction":""}}
  ],
  "compliance_score": 85
}}
compliance_score is 0-100 (100 = perfect compliance).
"""

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def style_node(state: ReviewState):
    llm = ChatGroq(
        model=model_name,
        temperature=0,
        api_key=api_key,
    )

    prompt = ChatPromptTemplate.from_template(STYLE_PROMPT)
    chain = prompt | llm | StrOutputParser()

    content = chain.invoke({
        "chunks": json.dumps(state.chunks, indent=2)
    })

    if content:
        try:
            clean_content = content.strip().replace("```json", "").replace("```", "")
            result = json.loads(clean_content)
        except:
            result = {"findings": [], "compliance_score": 100}
    else:
        result = {"findings": [], "compliance_score": 100}

    return {
        "style": result.get("findings", []),
        "score": float(result.get("compliance_score", 100)),
    }
