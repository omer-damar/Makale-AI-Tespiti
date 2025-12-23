import google.generativeai as genai

# API Anahtarını buraya yapıştır
API_KEY = "AIzaSyBRtTZcMC5XaLp00KeenG5r8DLp8y-BB3U" 

genai.configure(api_key=API_KEY)

print("Erişilebilir Modeller Listeleniyor...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Hata: {e}")