import csv
import getpass
import pandas as pd
from osgeo import gdal, ogr, osr
from sqlalchemy import create_engine, MetaData
from shapely import wkb, wkt

# postgres settings
user = 'postgres'
password = getpass.getpass()
host = 'localhost'
port = '5432'
db = 'ais_test'

# use the create_counting_line.sql script to create a counting line between two 
# coordinates, in case there is no digital counting line yet. 'heerenveen_isct' 
# refers to the table in the database that contains the counting line near Heerenveen
intersect_table = 'heerenveen_isct'

# connect to postgres database
url = 'postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, db)
con = create_engine(url, client_encoding='utf8')

# dates within the month of June, starting at the first monday
begindates = ['2019-06-03 00:00:00', '2019-06-04 00:00:00', '2019-06-05 00:00:00', '2019-06-06 00:00:00', '2019-06-07 00:00:00', '2019-06-08 00:00:00', '2019-06-09 00:00:00', \
    '2019-06-10 00:00:00', '2019-06-11 00:00:00', '2019-06-12 00:00:00', '2019-06-13 00:00:00', '2019-06-14 00:00:00', '2019-06-15 00:00:00', '2019-06-16 00:00:00', \
    '2019-06-17 00:00:00', '2019-06-18 00:00:00', '2019-06-19 00:00:00', '2019-06-20 00:00:00', '2019-06-21 00:00:00', '2019-06-22 00:00:00', '2019-06-23 00:00:00', \
    '2019-06-24 00:00:00', '2019-06-25 00:00:00', '2019-06-26 00:00:00', '2019-06-27 00:00:00', '2019-06-28 00:00:00', '2019-06-29 00:00:00', '2019-06-30 00:00:00']

enddates = ['2019-06-04 00:00:00', '2019-06-05 00:00:00', '2019-06-06 00:00:00', '2019-06-07 00:00:00', '2019-06-08 00:00:00', '2019-06-09 00:00:00', '2019-06-10 00:00:00', \
    '2019-06-11 00:00:00', '2019-06-12 00:00:00', '2019-06-13 00:00:00', '2019-06-14 00:00:00', '2019-06-15 00:00:00', '2019-06-16 00:00:00', '2019-06-17 00:00:00', \
    '2019-06-18 00:00:00', '2019-06-19 00:00:00', '2019-06-20 00:00:00', '2019-06-21 00:00:00', '2019-06-22 00:00:00', '2019-06-23 00:00:00', '2019-06-24 00:00:00', \
    '2019-06-25 00:00:00', '2019-06-26 00:00:00', '2019-06-27 00:00:00', '2019-06-28 00:00:00', '2019-06-29 00:00:00', '2019-06-30 00:00:00', '2019-06-30 50:00:00']

# for every day in array above, calculate the amount of ships that pass the counting line
for index, begindate in enumerate(begindates):
    enddate = enddates[int(index)]

    create_track = """
        CREATE OR REPLACE VIEW track6 AS SELECT 
            ships.name,
            ships.vesseltype,
            ships.hazardouscargo,
            ships.speed_df,
            ships.orientation_df,
            ST_MakeLine(ships.geom ORDER BY timestamp) As geom
        FROM ships
        WHERE ST_Intersects(ST_SetSRID(
                    ST_MakeBox2D(St_MakePoint(5.710553, 52.844946), ST_MakePoint(6.9244598, 53.3310272)), 4326), ships.geom)
            AND ships.timestamp BETWEEN '{}' AND '{}'
        GROUP BY name, vesseltype, hazardouscargo, speed_df, orientation_df;
    """.format(begindate, enddate)

    create_distinct_table = """
        SELECT
            a.name,
            ST_NumGeometries(ST_Intersection(a.geom, b.geom)),
            a.vesseltype,
            a.hazardouscargo
        FROM
            track6 as a 
                INNER JOIN 
            {} as b
        ON
            ST_Intersects(a.geom, b.geom)
        GROUP BY
            a.name, a.vesseltype, a.hazardouscargo, a.geom, b.geom;
    """.format(intersect_table)

    con.execute(create_track)
    con.execute(create_distinct_table)  
    df_res = pd.read_sql_query(create_distinct_table, con=con)

    df_res.to_csv(r'D:\Users\krob\Documents\AIS\Scripts\output_rws\intersect_csv\intersect_heerenveen_{}juni.csv'.format(index + 3))
