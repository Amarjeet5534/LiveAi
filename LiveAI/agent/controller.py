from config import model
from agent.tools import web_search
from agent.memory import retrieve_memory

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text

def live_agent(question):

    memory_context = retrieve_memory(question)

    decision_prompt = f"""
    You are an AI agent.

    If the question requires latest real-time data,
    respond only with: SEARCH_REQUIRED

    Otherwise answer directly.

    Question: {question}
    """

    decision = ask_gemini(decision_prompt)

    if "SEARCH_REQUIRED" in decision:
        search_results = web_search(question)

        final_prompt = f"""
        Previous Memory:
        {memory_context}

        Use the verified search results below to answer accurately.

        Search Results:
        {search_results}

        Question: {question}

        Give a clear answer.
        """

        return ask_gemini(final_prompt)

    return ask_gemini(f"""
    Previous Memory:
    {memory_context}

    Question:
    {question}
    """)
