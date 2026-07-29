from google import genai

API_KEY = "AQ.Ab8RN6JRghz14mf8pw6IWMQccSeRG_4txfDmbd1p2D9TkB395g"

print("API KEY:", API_KEY)

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Reply with only the word OK"
)

print(response.text)