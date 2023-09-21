#!/usr/bin/env python3
import os
import sys
import csv
import pandas as pd
import numpy as np
from io import StringIO
import openai
import dotenv

# Load OpenAI API key so calls can be made to the API
config = dotenv.dotenv_values(".env")
openai.api_key = config['OPENAI_API_KEY']


# Fetch the file to be operated on from the command line and convert it into a pandas dataframe
file_in = sys.argv[1]
file_name = os.path.basename(file_in)
file = os.path.splitext(file_name)
path = os.path.normpath(file_in).split(os.path.sep)
if file[1] != '.csv':
    raise Exception('Input file must be a .csv file')
iter_num = int(sys.argv[2])
if iter_num <= 0:
    raise Exception("Number of runs to perform must be greater than 0")
if iter_num > 10:
    raise Exception("Number of runs to perform must be less than or equal to 10")
df_in = pd.read_csv(file_in)
df_in = df_in.iloc[:, :1]
df = df_in.replace(',|\"|\'|;|:|\.|!|/|’|\(|\)|[|]','', regex=True)
print("File and command line arguments fetched")


# Remove all strings less than 100 characters from the dataframe and put those strings into their own
df_short = df.loc[df[df.columns[0]].str.len()<150]
df = df.loc[df[df.columns[0]].str.len()>=150]


# Remove all strings more than 500 characters from the dataframe and put those strings into their own
df_long = df.loc[df[df.columns[0]].str.len()>500]
df = df.loc[df[df.columns[0]].str.len()<=500]


# Split the dataframes into smaller sized dataframes, if the initial dataframe is too large
df_len = len(df)
if df_len > 10:
     dfs = np.array_split(df, -(df_len//-10), axis=0)
else:
    dfs = [df]

df_short_len = len(df_short)
if df_short_len > 10:
    dfs_short = np.array_split(df_short, -(df_short_len//-10), axis=0)
    for short in dfs_short:
        dfs.append(short)
elif 0 < df_short_len <= 10:
    dfs.append(df_short)

df_long_len = len(df_long)
if df_long_len > 5:
    dfs_long = np.array_split(df_long, -(df_long_len//-5), axis=0)
    for long in dfs_long:
        dfs.append(long)
elif 0 < df_long_len <= 5:
    dfs.append(df_long)

dfs_out = []
print("Input data parsed and formatted for processing")


# If the inputted csv file is too long, we split it into portions and run the program once for each portion, then merge the resulting data at the end
for df in dfs:
    df_init = df.copy()
    df_init_len = str(len(df_init))
    sent_num, them_num, file_num = 1, 1, 1
    for x in range(iter_num):
        print("Starting iteration " + str(x+1))
        try:
            # Write the prompt for the sentiment analysis function, using the entire csv file at once
            # Send the prompt to the chat bot and record the response to the 'sentiment' list
            prompt = """In one word, does each sentence in the following list have a positive, negative, or neutral sentiment. 
                        The list has {} sentences, so there should be exactly {} words. 
                        Output should be a comma seperated list: \n""".format(df_init_len, df_init_len) + df_init.to_csv(index=False, header=False)
            response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                )
            sentiment = response['choices'][0]['message']['content'].split(',')
            sentiment = [s.strip(' ') for s in sentiment]
            sentiment = [x.lower() for x in sentiment]
    
            
            # Save the responses to the pandas dataframe
            while 'Sentiment {}'.format(sent_num) in df.columns:
                sent_num += 1
            df['Sentiment {}'.format(sent_num)] = sentiment
            print("Finished sentiment analysis for rows " + str(df.index.values))

            # Write the prompt for the themes analysis function, using the entire csv file at once
            # Send the prompt to the chat bot and record the response to the 'themes' list
            prompt = """Give the three most common themes in one word for each of the {} sentences in the list below.
                        Sentences are delimited by new lines. Even if a sentence is short, output exactly three themes.
                        You should output exactly {} sets of themes. Do not output more or less than {} rows.
                        Output should be a comma seperated list with exactly three comma seperated themes per row. Follow your instructions exactly: 
                        \n""".format(df_init_len, df_init_len, df_init_len) + df_init.to_csv(index=False, header=False)
            response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                )
            themes = [response['choices'][0]['message']['content']]
            

            # Reformat the data retrieved from the themes prompt into a format suitable for the dataframe
            split = []
            for t in themes:
                split += [t.split('\n')]
            theme1, theme2, theme3 = [], [], []
            for s in split:
                for t in s:
                    t = t.split(',')
                    t = [s.strip(' ') for s in t]
                    t = [x.lower() for x in t]
                    ts = ['none', 'none', 'none']
                    if len(t) > 3:
                        break
                    for i in range(len(t)):
                        ts[i] = t[i]
                    theme1 += [ts[0]]
                    theme2 += [ts[1]]
                    theme3 += [ts[2]]


            # Save the responses to the pandas dataframe
            while 'Theme {}'.format(them_num) in df.columns:
                them_num += 1
            df['Theme {}'.format(them_num)] = theme1
            them_num += 1
            df['Theme {}'.format(them_num)] = theme2
            them_num += 1
            df['Theme {}'.format(them_num)] = theme3
            pass


        # If the AI returns malformed data that is unusable, catch the error and move on
        except ValueError:
            print("\nValueError exception for dataframe containing rows \n" + str(df.index.values) + "\n")
            continue
    dfs_out.append(df)


# Merge the outputted dataframes back togther into a single dataframe
df_out = pd.DataFrame()
while len(dfs_out) != 0:
    df_out = pd.concat([df_out, dfs_out.pop()])
df_out = df_out.sort_index()
head = [list(df_out.columns)[0]]
headers = list(df_out.columns)[1:]
headers.sort()
headers = head + headers
df_out = df_out[headers]
print("Merged all output dataframes back into one dataframe")


# Write the prompt for the summary function, using the entire csv file at once
# Send the prompt to the chat bot and record the response to the 'summary' list
prompt = """Write a paragraph that summarizes the data in the following csv file. 
            Specifically, you should answer with respect to the original question, {} 
            Make certain to address both the themes of the responses and the overall sentiment.
            """.format(df_out.columns[0]) + df_out.to_csv(index=False)
response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )
summary = [response['choices'][0]['message']['content']]


# Save the responses to the pandas dataframe 
df_out['Summary'] = pd.Series(summary)
print("Finished summary analysis on dataframe")


# Find the percentage of responses that share a sentiment value and add those percentage to the dataframe
sum_sent = []
df_sent = pd.DataFrame()
for head in headers:
    if head[:-2] == 'Sentiment':
        for h in df_out[head]:
            sum_sent.append(h)
v, c = np.unique(sum_sent, return_counts=True)
df_sent['Sentiment Values'], df_sent['Sentiment Totals'], df_sent['Sentiment Percentages']  = pd.Series(v), pd.Series(c), pd.Series((c/len(sum_sent))*100)
df_out = pd.concat([df_out, df_sent], axis=1)
print("Statistical analysis of sentiment analysis responses completed")


# Find the percentage of responses that share a theme value and add those percentage to the dataframe
sum_them = []
df_them = pd.DataFrame()
for head in headers:
    if head[:-2] == 'Theme':
        for h in df_out[head]:
            sum_them.append(h)
v, c = np.unique(sum_them, return_counts=True)
df_them['Theme Values'], df_them['Theme Totals'], df_them['Theme Percentages']  = pd.Series(v), pd.Series(c), pd.Series((c/len(sum_them))*100)
df_out = pd.concat([df_out, df_them], axis=1)
print("Statistical analysis of theme analysis responses completed")


# Save the dataframe as a csv file in a subfolder of the files out folder with the same name as the input file
if not os.path.exists('files_out\\' + path[1]):
    os.mkdir('files_out\\' + path[1])
if not os.path.exists('files_out\\' + path[1] + '\\' + file[0]):
    os.mkdir('files_out\\' + path[1] + '\\' + file[0])
while os.path.exists('files_out\\' + path[1] + '\\' + file[0] + '\\' + file[0] + ' v' + str(file_num) + '.csv'):
    file_num += 1
file_out = 'files_out\\' + path[1] + '\\' + file[0] + '\\' + file[0] + ' v' + str(file_num) + '.csv'
df_out.iloc[:, :1] = df_in.iloc[:, :1]
df_out.to_csv(file_out)
print("Run completed, output saved to " + file_out)