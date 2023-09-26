#!/usr/bin/env python3
import os
import sys
import pandas as pd
import openai
import dotenv
import glob


def main():
    # Load OpenAI API key so calls can be made to the API
    config = dotenv.dotenv_values(".env")
    openai.api_key = config['OPENAI_API_KEY']
    
    
    tries = 3


    # Fetch the folder to be operated on from the command line and convert it into a pandas dataframe
    folder_in = sys.argv[1]
    path = os.path.normpath(folder_in).split(os.path.sep)


    # Sanity check input and format output directory
    if not os.path.exists(folder_in):
        raise Exception('Input folder does not exist')
    if not os.path.exists('summaries\\' + path[1]):
        os.mkdir('summaries\\' + path[1])
    if not os.path.exists('summaries\\' + path[1] + '\\' + path[2]):
        os.mkdir('summaries\\' + path[1] + '\\' + path[2])
    for f in os.listdir('summaries\\' + path[1] + '\\' + path[2]):
        if not f.endswith('.csv'):
            continue
        os.remove(os.path.join('summaries\\' + path[1] + '\\' + path[2], f))


    # Read in the files from the input folder and format them
    files_in = []
    for fname in glob.glob(folder_in + '/*.csv'):
        file_in = pd.read_csv(fname)
        files_in += [file_in]    
    print("All files fetched and formatted")


    summaries = []
    for df in files_in:
        if not df['Summary'].empty:
            summaries += [df['Summary'].dropna()]
    df = pd.DataFrame(summaries)
    print("Summaries extracted and consolidated to one dataframe")


    iter = 0
    for iter in range(tries):
        try:
            # Write the prompt for the summary function, using the entire csv file at once
            # Send the prompt to the chat bot and record the response to the 'summary' list
            prompt = """Write a paragraph that summarizes the individual summaries in the following csv file. 
                        """ + df.to_csv(index=False)
            print("Starting summary analysis")
            response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                )
            summary = [response['choices'][0]['message']['content']]
            df_out = pd.DataFrame(summary)
            print("Finished summary analysis on dataframe")

        # If the AI returns malformed data that is unusable, catch the error and move on
        except KeyboardInterrupt:
            print("KeyboardInterrupt recieved, aborting process")
            sys.exit()
        except:
            e = sys.exc_info()
            if iter < tries - 1:
                print("\n{} exception in summary for dataframe containing \n{}\n".format(e[1], str(df)))
                print("Retrying {} out of {} tries\n".format(iter+1, tries))
                continue
            else:
                print("\n{} exception in summary could not be resolved\n".format(e[1]))
                break
        break


    # Save the dataframe as a csv file in a subfolder of the files out folder with the same name as the input file
    file_out = 'summaries\\' + path[1] + '\\' + path[2] + '\\' + path[2] + '.csv'
    df_out.to_csv(file_out)
    print("File finished, output saved to " + file_out)


if __name__ == '__main__':
    main()
        
