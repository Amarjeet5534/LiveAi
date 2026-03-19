from duckduckgo_search import DDGS

def web_search(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5)
        output = ""
        for r in results:
            output += r["title"] + "\n"
            output += r["body"] + "\n\n"
        return output
