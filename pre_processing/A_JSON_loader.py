import json
from json import JSONDecoder, JSONDecodeError
import re
import os
import tablib
from datetime import datetime

base_path = r"D:\Users\krob\Documents\AIS\rws_startdata\201906_ano_geofence.json"
out_path = r"D:\Users\krob\Documents\AIS\RWS_AIS_data\xaa_test"

def prepare_JSON ():
    """
    This function will prepare the JSON file in case JSON is stacked JSON. If JSON is already
    a nested JSON, skip this function and move directly to import_files().

    The function only appends a , after each line in the stacked JSON file. Depending on if and how you
    split the initial JSON file, please manually control the file endings before moving on to 
    import_files().
    """
    with open (base_path, 'r') as jfile, open(out_path, 'w') as joutfile:
        decoder = json.JSONDecoder()
        for index, line in enumerate(jfile):
            newline = line.replace(r'}}', r'}},')
            newline = newline.rstrip()

def import_files():
    base_path = r"D:\Users\krob\Documents\AIS\RWS_AIS_data"
    for counter, filen in enumerate(os.listdir(base_path)):
        with open(r"{}\{}".format(base_path, filen), 'r') as json_file:
            print('file number {}'.format(filen))

            data = json.load(json_file)
            print('loaded the JSON!')

            headers = ('name', 'timestamp', 'longitude', 'latitude', 'width', 'length', 'vesseltype', 'hazardouscargo')
            table = tablib.Dataset(headers=headers)

            for index, record in enumerate(data):
                if 'positionmessage' in record:
                    name = record['positionmessage']['name']
                    if '2019' in record['positionmessage']['timestamplast']:
                        time = record['positionmessage']['timestamplast']
                        time = time.replace('T', ' ')
                        time = time.replace('Z', '')
                        time = datetime.strptime(time, r'%Y-%m-%d %H:%M:%S')
                    longitude = record['positionmessage']['longitude']
                    longitude = float(longitude)
                    latitude = record['positionmessage']['latitude']
                    latitude = float(latitude)
                    width = float(record['positionmessage']['width']) if 'width' in record else 'Null'
                    length = float(record['positionmessage']['length']) if 'length' in record else 'Null'
                    vesseltype = int(record['positionmessage']['vesseltype'])
                    hazardouscargo = int(record['positionmessage']['hazardouscargo'])

                    # print(index, name, time, longitude, latitude, width, length, vesseltype, hazardouscargo)
                    table.append([name, time, longitude, latitude, width, length, vesseltype, hazardouscargo])


            pddata = (table.export('df')).dropna()
            pddata.to_csv(r'D:\Users\krob\Documents\AIS\Scripts\output_rws\initial_csv\JSON_{}.csv'.format(counter + 9), sep=',')

prepare_JSON()
import_files()
