#!/usr/bin/env python3
import os
import sys
import csv
import pandas as pd

def main():
    # Import file size from command line
    file_size = int(sys.argv[2])

    # Import input file location from the command line
    file_in = sys.argv[1]
    file_name = os.path.basename(file_in)
    file = os.path.splitext(file_name)
    path = os.path.normpath(file_in).split(os.path.sep)
    if file[1] != '.csv':
        raise Exception('Input file must be a .csv file')
    print("Read file from command line")
    # Create destination if it does not exist. Clean it of any output of previous runs
    if not os.path.exists('files_in\\' + path[1]):
        os.mkdir('files_in\\' + path[1])
    if not os.path.exists('files_in\\' + path[1] + '\\' + file[0]):
        os.mkdir('files_in\\' + path[1] + '\\' + file[0])
    for f in os.listdir('files_in\\' + path[1] + '\\' + file[0]):
        if not f.endswith('.csv'):
            continue
        os.remove(os.path.join('files_in\\' + path[1] + '\\' + file[0], f))
    
    # Write file with header and file_size number of rows
    def write_file(num, rows):
        print("Writing file")
        with open('files_in\\' + path[1] + '\\' + file[0] + '\\' + file[0] + ' ' + str(num) + '.csv', 'w') as f_out:
            f_out.write(header)
            f_out.writelines(rows)
            print("Wrote file to: " + 'files_in\\' + path[1] + '\\' + file[0] + '\\' + file[0] + ' ' + str(num) + '.csv')

    # Open the input file and initialize variables
    with open(file_in, 'r') as f_in:
        print("Splitting files")
        count = 0
        rs = []
        header = f_in.readline()
        # Import file_size number of rows, then write those rows after file_size number of iterations
        for r in f_in:
            count += 1
            rs.append(r)
            if count % file_size == 0:
                write_file(count // file_size, rs)
                rs = []
        # If there is any remainder rows after, write those rows
        if len(rs) > 0:
            write_file((count // file_size) + 1, rs)
        print("Run completed, output saved to: " + 'files_in\\' + path[1] + '\\' + file[0])

if __name__ == '__main__':
    main()
        
