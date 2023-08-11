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
df = df_in.replace(',|\"|\'|;|:|\.|!|/','', regex=True)
df_len = str(len(df))


# Write the prompt for the sentiment analysis function, using the entire csv file at once
# Send the prompt to the chat bot and record the response to the 'sentiment' list
prompt = """In one word, does each sentence in the following list have a positive or negative sentiment. 
            The list has {} sentences, so there should be exactly {} words. 
            Output should be a comma seperated list: \n""".format(df_len, df_len) + df.to_csv(index=False, header=False)
response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )
sentiment = response['choices'][0]['message']['content']
sentiment = sentiment.split(', ')


# Write the prompt for the themes analysis function, using the entire csv file at once
# Send the prompt to the chat bot and record the response to the 'themes' list
prompt = """Give the three most common themes in one word for each of the {} sentences in the list below.
            You should output exactly {} sets of themes. Do not output more or less than {} rows. 
            Output should be a comma seperated list with exactly three comma seperated themes per row. Follow your instructions exactly: 
            \n""".format(df_len, df_len, df_len) + df.to_csv(index=False, header=False)
print(prompt)
response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )
themes = [response['choices'][0]['message']['content']]
print(themes)

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
# sentiment = ['positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive']

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


# Reformat the data retrieved from the themes prompt into a format suitable for the dataframe
split = []
for t in themes:
    split += [t.split('\n')]

print(split)
print(len(split[0]))
theme1, theme2, theme3 = [], [], []
for s in split:
    for t in s:
        print(t)
        t = t.split(', ')
        theme1 += [t[0]]
        theme2 += [t[1]]
        theme3 += [t[2]]
print(theme1, '\n', theme2, '\n', theme3, '\n')
print(len(theme1), '\n', len(theme2), '\n', len(theme3), '\n')

# Save the responses to the pandas dataframe and save the dataframe as a csv file in the files out folder with the same name as the input file
df['Sentiment'] = sentiment
df['Theme 1'] = theme1
df['Theme 2'] = theme2
df['Theme 3'] = theme3

file_out = 'files_out\\' + file_in[9:]
df.to_csv(file_out, index=None)