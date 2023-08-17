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


# List of keywords we want the AI to not output
ignore = ['favorite', 'charitable', 'giving', 'gift', 'positive']

# Fetch the file to be operated on from the command line and convert it into a pandas dataframe
file_in = sys.argv[1]
iter_num = int(sys.argv[2])
df_in = pd.read_csv(file_in)
df = df_in.replace(',|\"|\'|;|:|\.|!|/','', regex=True)
df_len = len(df)


# Remove all strings less than 100 characters from the dataframe and put those strings into their own
# Split the dataframe into smaller sized dataframes, if the initial dataframe is too large
df_short = df.loc[df[df.columns[0]].str.len()<100]
df = df.loc[df[df.columns[0]].str.len()>=100]
if df_len > 10:
     dfs = np.split(df, [df_len//2], axis=0)
dfs.append(df_short)
dfs_out = []


# If the inputted csv file is too long, we split it into portions and run the program once for each portion, then merge the resulting data at the end
for df in dfs:
    df_init = df.copy()
    df_init_len = str(len(df_init))
    sent_num, them_num, file_num = 1, 1, 1
    for x in range(iter_num):
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

        # sentiment = ['positive', 'positive', 'negative', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive']
        # sentiment = ['positive', 'positive', 'negative', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive']
        # if not len(df) == len(sentiment):
            # sentiment = ['positive', 'positive', 'negative', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive', 'positive']
        
        
        # Save the responses to the pandas dataframe
        while 'Sentiment {}'.format(sent_num) in df.columns:
            sent_num += 1
        df['Sentiment {}'.format(sent_num)] = sentiment

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
        
        
        # themes = ["successful, positive, rewarding\ncharitable, giving, results\nfavorite, experience, pleasant\nChristmas cards, donation, website\nlump sum, ministry, church\ncomfort, helping, less fortunate\nupdates, rewarding, pediatric oncology\nlocal homeless shelter, meaningful, gift\nexperiences, education, denied\nsupporting a child, mission trip, favorite\nFriends of Kids with Cancer, gift cards, support\nChristmas drive, underprivileged children, wrap presents\nsponsorship, World Vision, meaningful\nFoster kid party, Santa, crafts\nplayground, special needs children, fulfilling\ngiving, personal impact, love\nHope House, Nspire, homeless women and children\nsalvation army, financial support, Christmas\nAfrican Well Fund, builds wells, tangible need\nlibrary's fundraiser, dressed up, celebrate reading\nChristmas toys, low income communities, children\nhelping others, important, without knowing\nALS research, best friend, courage"]
        # themes = ["successful, positive, rewarding\ncharitable, giving, results\nfavorite, experience, pleasant\nChristmas cards, donation, website\nlump sum, ministry, church\ncomfort, helping, less fortunate\nupdates, rewarding, pediatric oncology\nlocal homeless shelter, meaningful, gift\nexperiences, education, denied\nsupporting a child, mission trip, favorite\nFriends of Kids with Cancer, gift cards, support"]
        # if len(df) == 12:
        #     themes = ["successful, positive, rewarding\ncharitable, giving, results\nfavorite, experience, pleasant\nChristmas cards, donation, website\nlump sum, ministry, church\ncomfort, helping, less fortunate\nupdates, rewarding, pediatric oncology\nlocal homeless shelter, meaningful, gift\nexperiences, education, denied\nsupporting a child, mission trip, favorite\nFriends of Kids with Cancer, gift cards, support\nChristmas drive, underprivileged children, wrap presents"]
        

        # Reformat the data retrieved from the themes prompt into a format suitable for the dataframe
        split = []
        for t in themes:
            split += [t.split('\n')]
        theme1, theme2, theme3 = [], [], []
        for s in split:
            for t in s:
                t = t.split(', ')
                ts = ['None', 'None', 'None']
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
# summary = ['The charities supported by the respondents in the csv file perform a wide range of work. Some of the common themes include providing support to the homeless, supporting healthcare organizations, helping children in need, and supporting educational institutions. The overall sentiment towards the work performed by these charities is positive, with respondents expressing feelings of fulfillment, reward, and satisfaction. However, there are also mentions of negative sentiment, particularly in relation to the lack of support for certain causes or organizations.']


# Save the responses to the pandas dataframe 
df_out['Summary'] = pd.Series(summary)


# Save the dataframe as a csv file in a subfolder of the files out folder with the same name as the input file
if not os.path.exists('files_out\\' + file_in[9:-4]):
    os.mkdir('files_out\\' + file_in[9:-4])
while os.path.exists('files_out\\' + file_in[9:-4] + '\\' + file_in[9:-4] + ' v' + str(file_num) + '.csv'):
        file_num += 1
file_out = 'files_out\\' + file_in[9:-4] + '\\' + file_in[9:-4] + ' v' + str(file_num) + '.csv'
df_out.to_csv(file_out)