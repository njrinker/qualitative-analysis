import os
import csv
import openai
import dotenv

config = dotenv.dotenv_values(".env")
openai.api_key = config['OPENAI_API_KEY']

prompts = ["Give a one word sentiment analysis of the following statement: Pizza is tasty.",
           "Create a two-column CSV of top science fiction movies along with the year of release.",
           "Create a three-column CSV of top science fiction movies along with the year of release and the total amount grossed.",
           "Create a 4-column CSV of top science fiction movies along with the year of release, the total amount grossed, and audience rating."]

for p in prompts:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": p},
        ],
        temperature=0.6,
        max_tokens=128
    )
    print("\n"+p)
    print(response['choices'][0]['message']['content'])
