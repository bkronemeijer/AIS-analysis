#extracting tracks out of concatenated csv based on mmsi number
import pandas as pd

def extract_tracks():
    filen = r'D:\Users\krob\Documents\AIS\Scripts\output_rws\concatenated_csv.csv'

    #read over all csv files and create seperate csv files based on mmsi
    df1 = pd.read_csv(filen, sep = ',')

    df1_name_accumulator = (df1['name'].unique()).tolist()

    for counter, value in enumerate(df1_name_accumulator):
        df1[df1['name'] == value].to_csv(r'D:\Users\krob\Documents\AIS\Scripts\output_rws\mmsi_tracks\name={}.csv'.format(value), sep = ',', index = False)
