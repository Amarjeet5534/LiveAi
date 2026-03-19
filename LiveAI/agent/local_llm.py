import requests

def local_generate(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 80,   # short answers
                    "temperature": 0.6
                }
            }
        )
        return response.json()["response"]
    except:
        return "Local AI error."
