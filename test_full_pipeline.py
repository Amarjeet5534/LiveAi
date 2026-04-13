import asyncio
from voice.speech_to_text import record_audio, transcribe_audio
from voice.text_to_speech import speak
from agent.local_llm import local_generate
from agent.system_control import open_app, shutdown_pc, search_youtube, search_google, create_file

print("🚀 Neura AI Started - Listening...")

record_audio(duration=6)
question = transcribe_audio()

print("📝 You said:", question)

if not question.strip():
    print("⚠ No speech detected.")
else:
    # STEP 1: Fast keyword detection (no API call)
    question_lower = question.lower()
    tool_decision = None
    
    if any(word in question_lower for word in ["open", "launch", "start"]):
        # Extract app name
        words = question_lower.split()
        app_name = ""
        for i, word in enumerate(words):
            if word in ["open", "launch", "start"] and i + 1 < len(words):
                app_name = " ".join(words[i+1:])
                break
        if app_name:
            tool_decision = {"tool": "open_app", "arguments": {"app_name": app_name}}
    
    elif "shutdown" in question_lower or "turn off" in question_lower:
        tool_decision = {"tool": "shutdown_pc", "arguments": {}}
    
    elif "youtube" in question_lower and "search" in question_lower:
        query = question_lower.replace("search", "").replace("youtube", "").strip()
        tool_decision = {"tool": "search_youtube", "arguments": {"query": query}}
    
    elif "google" in question_lower and "search" in question_lower:
        query = question_lower.replace("search", "").replace("google", "").strip()
        tool_decision = {"tool": "search_google", "arguments": {"query": query}}
    
    if tool_decision:
        print(f"🔧 Routing to tool: {tool_decision['tool']}")
        tool_name = tool_decision['tool']
        args = tool_decision.get('arguments', {})
        
        # Execute tool
        result = None
        try:
            if tool_name == "open_app":
                result = open_app(args.get('app_name', ''))
            elif tool_name == "shutdown_pc":
                result = shutdown_pc()
            elif tool_name == "search_youtube":
                result = search_youtube(args.get('query', ''))
            elif tool_name == "search_google":
                result = search_google(args.get('query', ''))
            elif tool_name == "create_file":
                result = create_file(args.get('filename', ''), args.get('content', ''))
            
            if result:
                print(f"✅ {result}")
                asyncio.run(speak(result))
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            print(f"❌ {error_msg}")
            asyncio.run(speak(error_msg))
    else:
        # STEP 2: Use local Ollama for fast response
        print("🤖 Querying local Ollama...")
        answer = local_generate(question)
        answer = answer.strip() if answer else ""
        
        if answer:
            print("Ollama:", answer)
            asyncio.run(speak(answer))
        else:
            print("⚠ No response generated")
