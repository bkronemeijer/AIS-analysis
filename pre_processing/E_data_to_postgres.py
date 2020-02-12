""" 
postgres database: ais_test
postgres table: ships

this script inserts the csv file with all ais data into a postgres database with
a postgis extension

""" 

import psycopg2
import csv
import getpass
from sqlalchemy import create_engine, MetaData


# postgres settings
user = 'postgres'
password = getpass.getpass()
host = 'localhost'
port = '5432'
db = 'ais_test'

# connect to postgres database
url = 'postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, db)
con = create_engine(url, client_encoding='utf8')

with open(r"D:\Users\krob\Documents\AIS\Scripts\output_rws\concatenated_withcalc_nonsort.csv", 'r') as infile:
    reader = csv.reader(infile)
    next(reader, None)
    for row in reader:
        name = row[1]
        timestamp = row[2]
        longitude = float(row[3])
        latitude = float(row[4])
        width = None if row[5] == 'Null' else float(row[5])
        length = None if row[6] == 'Null' else float(row[6])
        vesseltype = None if row[7] == '' else int(row[7])
        hazardouscargo = None if row[8] == '' else int(row[8])
        speed = None if row[9] == '' else float(row[9])
        orientation = None if row[10] == '' else float(row[10])
        window_speed = None if row[11] == '' else float(row[11])
        window_orientation = None if row[12] == '' else float(row[12])
        orientation_change = None if row[13] == '' else float(row[13])

        con.execute("INSERT INTO ships VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, timestamp, longitude, \
            latitude, width, length, vesseltype, hazardouscargo, speed, orientation, window_speed, window_orientation, orientation_change))
