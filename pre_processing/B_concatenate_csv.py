import glob
import pandas as pd
import csv
import os

def concat_csv():
    #concenate all B-rider tracks to one large file
    path = r'D:\Users\krob\Documents\AIS\Scripts\output_rws\mmsi_tracks_recalculated'
    all_files = glob.glob(path + "/*.csv")
    frame = pd.DataFrame()
    list_ = []
    for file_ in all_files:
        df = pd.read_csv(file_, sep=',')
        list_.append(df)
    frame = pd.concat(list_, sort=False)

    frame.to_csv(r'D:\Users\krob\Documents\AIS\Scripts\output_rws\concatenated_withcalc_nonsort.csv', sep = ',')
    print('csv concenated/created')
