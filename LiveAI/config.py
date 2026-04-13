import google.generativeai as genai

genai.configure(api_key="AIzaSyB4-lwD7pGE1ZoFViL-hmK5tLYbJW8kbVM")

model = genai.GenerativeModel("gemini-2.5-flash")
