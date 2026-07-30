from google import genai

API_KEY = "AQ.Ab8RN6JRghz14mf8pw6IWMQccSeRG_4txfDmbd1p2D9TkB395g"

client = genai.Client(api_key=API_KEY)

for model in client.models.list():
    print(model.name)