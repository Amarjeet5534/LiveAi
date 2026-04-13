import json
from config import model

def decide_tool(user_input):
    prompt = f"""
You are an AI tool router.

Available tools:
1. open_app(app_name)
2. shutdown_pc()
3. search_youtube(query)
4. search_google(query)
5. create_file(filename, content)

If a tool is required, respond ONLY in valid JSON:
{{
  "tool": "tool_name",
  "arguments": {{}}
}}

If no tool is required, respond with:
NONE

User request:
{user_input}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        if text.upper() == "NONE":
            return None

        # Remove accidental markdown
        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception:
        return None
