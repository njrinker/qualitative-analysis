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
df_in = pd.read_csv(file_in)
df = df_in.replace(',|\"|\'|;|:|\.','', regex=True)
print(df.to_csv())
prompt = "In one word, is each sentence in the following file positive or negative: \n" + df.to_csv(index=False, header=False)
response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        # max_tokens=128
    )
print(response['choices'][0]['message']['content'])
responses = response['choices'][0]['message']['content']
# responses = "positive, positive, negative, positive, positive, positive, positive, positive, positive, positive, positive, positive, positive, positive, positive, positive, positive, positive, positive, positive, positive, positive"
print(responses)
responses = responses.split(', ')
print(responses)
print(len(responses))
# # Create an empty list to store responses in and iterate over ever row in the inputted csv file
# sentiment = []
# for row in df.itertuples():
#     # Construct prompt with instructions on what the AI should do with the provided data
#     prompt = "Is this sentence positive or negative in one word: " + row[1]
#     # Make an API call to the chat bot with the given prompt and save the response
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "user", "content": prompt},
#         ],
#         temperature=0.5,
#         # max_tokens=128
#     )
#     sentiment += [response['choices'][0]['message']['content']]
sentiment = ['positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive']

# # Create an empty list to store responses in and iterate over ever row in the inputted csv file
# themes = []
# for row in df.itertuples():
#     # Construct prompt with instructions on what the AI should do with the provided data
#     prompt = "Give the three themes of this sentence in one word each, seperated by commas: " + row[1]
#     # Make an API call to the chat bot with the given prompt and save the response
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "user", "content": prompt},
#         ],
#         temperature=0.5,
#         # max_tokens=128
#     )
#     themes += [response['choices'][0]['message']['content']]
themes = ['projects, success, rewarding', 'Seeing, results, charitable', 'difficult, favorite, experience', 'receiving, donating, understanding', 'Giving, lump sum, church', 'comfort, knowing, helping', 'think, updates, rewarding', 'friendship, generosity, alternative', 'charitable experience, donation, opportunity', 'favorite experience, supporting, meeting', 'favorite, Friends of Kids with Cancer, organization', 'charitable giving, Christmas drive, underprivileged children', 'sponsorship, meaningful, impact', 'Celebration, Giving, Involvement', 'honoring, special, fulfilling', 'love, giving, impact', 'charities, recipients, donations', 'favorite, charitable, giving', 'enjoyment, donations, well-building', 'fundraiser, celebration, donation', 'Providing, Christmas, toys', 'Feeling, helping, judgment', 'favorite, ALS research, example']

# Reformat the data retrieved from the themes prompt into a format suitable for the dataframe
split = []
for t in themes:
    split += [t.split(', ')]

theme1, theme2, theme3 = [], [], []
for s in split:
    theme1 += [s[0]]
    theme2 += [s[1]]
    theme3 += [s[2]]

# Save the responses to the pandas dataframe and save the dataframe as a csv file in the files out folder with the same name as the input file
df['Sentiment'] = sentiment
df['Theme 1'] = theme1
df['Theme 2'] = theme2
df['Theme 3'] = theme3

file_out = 'files_out\\' + file_in[9:]
df.to_csv(file_out, index=None)