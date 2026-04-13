import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(user, assistant):

    memory = load_memory()

    memory.append({
        "user": user,
        "assistant": assistant
    })

    memory = memory[-20:]

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)


def memory_context():

    memory = load_memory()

    text = ""

    for m in memory:
        text += f"User: {m['user']}\nAssistant: {m['assistant']}\n"

    return text
