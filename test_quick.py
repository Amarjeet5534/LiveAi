import asyncio
from agent.local_llm import local_generate
from agent.system_control import open_app

print("⚡ Quick Speed Test\n")

# Test 1: Fast tool detection
print("TEST 1: Tool Detection")
question = "open chrome"
question_lower = question.lower()

if any(word in question_lower for word in ["open", "launch", "start"]):
    words = question_lower.split()
    app_name = ""
    for i, word in enumerate(words):
        if word in ["open", "launch", "start"] and i + 1 < len(words):
            app_name = " ".join(words[i+1:])
            break
    if app_name:
        print(f"✅ Detected: open_app('{app_name}')")
        print(f"Opening {app_name}...")
        result = open_app(app_name)
        print(f"Result: {result}\n")

# Test 2: Ollama response
print("TEST 2: Ollama Response")
test_question = "What is 2+2?"
print(f"Question: {test_question}")
answer = local_generate(test_question)
print(f"Answer: {answer}\n")

print("✅ Tests completed!")
