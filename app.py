import os
import sys
import csv
import pandas as pd
from io import StringIO
import openai
import dotenv

# Load OpenAI API key so calls can be made to the API
config = dotenv.dotenv_values(".env")
openai.api_key = config['OPENAI_API_KEY']

# Fetch the file to be operated on from the command line and convert it into a pandas dataframe
file_in = sys.argv[1]
df = pd.read_csv(file_in, header=None).tail(-1)

# prompts = ["Give a one word sentiment analysis of the following statement: Pizza is tasty.",
#            "Create a two-column CSV of top science fiction movies along with the year of release.",
#            "Create a three-column CSV of top science fiction movies along with the year of release and the total amount grossed.",
#            "Create a 4-column CSV of top science fiction movies along with the year of release, the total amount grossed, and audience rating."]

# Construct the list of different prompts with instructions on what the AI should do with the provided data
prompts = ["Give a one word sentiment analysis for each statement in a row of the following csv file where there are " + str(df.shape[0]) + " rows so there should only be " + str(df.shape[0]) + " responses: \n" + df.to_csv(index=False, header=False)]

# Create a for each loop for each individual prompt in prompts. Then, make an API call to the chat bot and save the response
# for p in prompts:
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "user", "content": p},
#         ],
#         temperature=0.5,
#         # max_tokens=128
#     )
#     print("\n"+p)
#     print(response['choices'][0]['message']['content'])
#     responses = response['choices'][0]['message']['content']

responses = 'successful, rewarding, harder, positive, pleasant, loved, quick, easy, beautiful, great, lump, specific, comfort, rewarding, favorite, meaningful, enjoyed, favorite, available, favorite, meaningful, incredible, fulfilling, love, favorite, enjoyed, takes, chance, great, low, feeling, important, favorite'
responses = responses.split(', ')
print(len(responses))
print(responses)
responses = responses[:df.shape[0]]
print(len(responses))
print(responses)

# Save the responses to the pandas dataframe and save the dataframe as a csv file in the files out folder with the same name as the input file
df['Sentiment'] = responses
file_out = 'files_out\\' + file_in[9:]
print(file_out)
df.to_csv(file_out, index=False, header=False)