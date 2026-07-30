from google import genai

client = genai.Client(api_key="AQ.Ab8RN6JRghz14mf8pw6IWMQccSeRG_4txfDmbd1p2D9TkB395g")

response = client.models.generate_content(
    model="models/gemini-3.5-flash",
    contents="Say Hello"
)

print(response.text)