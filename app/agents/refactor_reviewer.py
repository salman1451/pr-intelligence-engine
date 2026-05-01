import os
import json
from app.models.schemas import ReviewState
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

REFACTOR_PROMPT = """
You are a senior software architect reviewing code for maintainability.
Suggest refactoring improvements, not style issues and not security bugs.

Code Chunks:
{chunks}

Look for: functions >50 lines, duplicated logic, complex conditionals,
magic numbers, missing abstractions, poor separation of concerns.

Output ONLY valid JSON:
{{
  "suggestions": [
    {{"type":"simplify|extract|rename|pattern","description":"","affected_lines":[]}}
  ]
}}
"""

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "llama3-70b-8192")


def refactor_node(state: ReviewState):
    llm = ChatGroq(
        model=model_name,
        temperature=0,
        api_key=api_key,
    )

    prompt = ChatPromptTemplate.from_template(REFACTOR_PROMPT)
    chain = prompt | llm | StrOutputParser()

    content = chain.invoke({
        "chunks": json.dumps(state.chunks, indent=2)
    })

    if content:
        try:
            clean_content = content.strip().replace("```json", "").replace("```", "")
            result = json.loads(clean_content)
        except:
            result = {"suggestions": []}
    else:
        result = {"suggestions": []}

    return {
        "refactor": result.get("suggestions", []),
    }
