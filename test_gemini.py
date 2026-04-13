from config import model

response = model.generate_content("Reply with: Gemini integration successful")
print(response.text)
