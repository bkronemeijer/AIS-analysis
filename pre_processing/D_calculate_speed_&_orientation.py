import re
import os
import glob
import pandas as pd
import pyproj
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime, timedelta


def calculate_time(point, next_point):
    current_time = datetime.strptime(point['timestamp'], r'%Y-%m-%d %H:%M:%S')
    next_time = datetime.strptime(next_point['timestamp'], r'%Y-%m-%d %H:%M:%S')

    passed_time = next_time - current_time

    return passed_time

def calculate_orientation(point, next_point):
    lon1 = (point['longitude'])
    lat1 = (point['latitude'])
    lon2 = (next_point['longitude'])
    lat2 = (next_point['latitude'])

    # lon1 = float(lon1)
    # lat1 = float(lat1)
    # lon2 = float(lon2)
    # lat2 = float(lat2)

    # dot = lon1*lon2 + lat1*lat2
    # determinant = lon1*lat2 - lon2*lat1
    # angle = atan2(determinant, dot)

    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth, back_azimuth, distance = geodesic.inv(lat1, lon1, lat2, lon2)

    return distance, fwd_azimuth

def append_data(step=1, calc_type='regular'):
    for index, point in df.iloc[:-step].iterrows():
        next_point = df.iloc[index + step]

        passed_time = calculate_time(point, next_point)
        distance = calculate_orientation(point, next_point)[0]

        if passed_time.total_seconds() > 0:
            speed = (distance / passed_time.total_seconds()) * 3.6
        else:
            speed = 0

        orientation = calculate_orientation(point, next_point)[1]
        if orientation < 0:
            orientation = 360 + orientation

        header = ''
        if calc_type == 'window':
            header = 'window_'

        df.loc[index, '{}speed_df'.format(header)] = speed
        df.loc[index, '{}orientation_df'.format(header)] = orientation

def calc_orientation_derivative():
    for index, point in df.iloc[:-1].iterrows():
        next_point = df.iloc[index + 1]

        orientation_change = next_point['orientation_df'] - point['orientation_df']
        df.loc[index, 'orientation_change'] = orientation_change

def calculate_and_append_speed_and_orientation():
    base_path = r'D:\Users\krob\Documents\AIS\Scripts\output_rws\mmsi_tracks'
    all_files = glob.glob(base_path + "/*.csv")
    all_calculated_files = r'D:\Users\krob\Documents\AIS\Scripts\output\mmsi_tracks_recalculated'

    for filen in all_files:
        ship_nr = (re.findall(r'(\d+)', filen))[0]
        if os.path.exists(all_calculated_files + '/shipNr={}.csv'.format(ship_nr)) == False:
            df = (pd.read_csv(filen, sep=',')).sort_values(by=['timestamp'], kind='mergesort')
            window_step = 4
            del df['Unnamed: 0']
            del df['Unnamed: 0.1']
            print('deleted unnecessary columns')
            df = (df.drop_duplicates(subset='timestamp')).reset_index(drop=True)
            print('dropped duplicates')
            
            if df.shape[0] > window_step:
                append_data()
                print('appended data')
                append_data(window_step, 'window')
                print('appended window data')
                calc_orientation_derivative()
                print('appended orientation derivative')

            # print(df)
            print('creating csv for ship {}'.format(ship_nr))

            df.to_csv(r'D:\Users\krob\Documents\AIS\Scripts\output_rws\mmsi_tracks_recalculated\shipNr={}.csv'.format(ship_nr), sep=',', index=False)
