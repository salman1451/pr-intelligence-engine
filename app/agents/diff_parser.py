import os
import json
from app.models.schemas import ReviewState
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

DIFF_PROMPT = """
You are a code diff analysis expert. Parse the GitHub PR diff into structured JSON.

PR Title: {pr_title}
PR Description: {pr_description}
Raw Diff:
{raw_diff}

Output ONLY valid JSON:
{{
  "changed_files": [{{"path":"","change_type":"added|modified|deleted|renamed","language":"","lines_added":0,"lines_removed":0}}],
  "parsed_chunks": [{{"file":"","chunk_type":"function|class|import|config|test|other","description":"","added_lines":[],"removed_lines":[],"context_lines":[]}}]
}}
"""

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "llama3-70b-8192")


def parse_diff_node(state: ReviewState):
    llm = ChatGroq(
        model=model_name,
        temperature=0,
        api_key=api_key,
    )

    prompt = ChatPromptTemplate.from_template(DIFF_PROMPT)
    chain = prompt | llm | StrOutputParser()

    content = chain.invoke({
        "pr_title": state.title,
        "pr_description": state.desc,
        "raw_diff": state.raw_diff[:8000]
    })

    parse_error = False
    if content:
        try:
            clean_content = content.strip().replace("```json", "").replace("```", "")
            diff = json.loads(clean_content)
            if not diff.get("changed_files") and not diff.get("parsed_chunks"):
                parse_error = True
        except:
            diff = {}
            parse_error = True
    else:
        diff = {}
        parse_error = True

    return {
        "files": diff.get("changed_files", []),
        "chunks": diff.get("parsed_chunks", []),
        "parse_error": parse_error
    }


TEXT_ONLY_LANGUAGES = {"text", "markdown"}


def should_analyze_code(state: ReviewState):
    if state.parse_error:
        return "skip"
        
    for file in state.files:
        language = file.get("language", "").lower()
        if language != "" and language not in TEXT_ONLY_LANGUAGES:
            return "analyze"
    return "skip"