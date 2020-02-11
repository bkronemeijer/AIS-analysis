######################################################################
# postgres database: ais_test
# initial postgres table: ships

# this script selects all ships with dangerous cargo and extracts
# stops and moves per ship and returns a shapefile containing the 
# stops and moves of each ship
######################################################################

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

# connect to postgres database
url = 'postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, db)
con = create_engine(url, client_encoding='utf8')

# selection criteria
begindate = '2019-06-09 00:00:00'
enddate = '2019-06-10 00:00:00'

# extract all ship names that are considered hazardous cargo
hazardous_query = '''
    SELECT DISTINCT name 
        FROM ships
    WHERE hazardouscargo NOT IN (5)
    ORDER BY name ASC
'''

df = pd.read_sql_query(hazardous_query, con=con)
haz_list = df['name'].tolist()

for idx, ship in enumerate(haz_list):
    old_ship = ship
    ship = ship.replace('-', '_')

    # queries to be performed on each ship
    drop_table = 'DROP TABLE IF EXISTS {}_result'.format(ship)

    create_table = """
        CREATE TABLE {}_result AS SELECT * FROM ships
        WHERE name = '{}'
        ORDER BY name, timestamp
    """.format(ship, old_ship)

    set_geom1 = 'ALTER TABLE {}_result ADD COLUMN geom_meter geometry'.format(ship)
    set_geom2 = 'UPDATE {}_result SET geom_meter = geom'.format(ship)
    set_geom3 = """
        ALTER TABLE {}_result
            ALTER COLUMN geom_meter TYPE geometry(Point, 4978)
            USING ST_Transform(geom_meter, 4978)
    """.format(ship)

    create_index = 'CREATE INDEX {}_geom_idx ON {}_result USING GIST(geom_meter)'.format(ship, ship)

    add_column1 = 'ALTER TABLE {}_result ADD COLUMN id SERIAL PRIMARY KEY'.format(ship)
    add_column2 = 'ALTER TABLE {}_result ADD COLUMN num_neighbours int'.format(ship)
    add_column3 = 'ALTER TABLE {}_result ADD COLUMN pause int'.format(ship)

    calc_neighbours = """
        UPDATE {}_result SET num_neighbours = agg.num_neighbours 
            FROM (
                SELECT count(b.id) as num_neighbours, a.id
                from {}_result a, {}_result b
                where st_dwithin(a.geom_meter, b.geom_meter, 3.5) and a.id != b.id group by a.id)
            agg
        where agg.id = {}_result.id
    """.format(ship, ship, ship, ship)

    set_pause1 = 'UPDATE {}_result SET pause = 1 WHERE num_neighbours >= 6'.format(ship)
    set_pause2 = 'UPDATE {}_result SET pause = COALESCE(pause, 0)'.format(ship)
    set_pause3 = """
        UPDATE {}_result SET pause = 1
        FROM (
            SELECT wl.timestamp, geom, pause
            FROM
                (SELECT name, timestamp,  geom, pause, lead(pause, 1) OVER (ORDER BY timestamp ASC) AS lead1, 
                                                lead(pause, 2) OVER (ORDER BY timestamp ASC) AS lead2, 
                                                lag(pause, 1) OVER (ORDER BY timestamp ASC) AS lag1, 
                                                lag(pause, 2) OVER (ORDER BY timestamp ASC) AS lag2
                FROM {}_result
                ORDER BY timestamp ASC) AS wl
            WHERE pause = 0 AND lead1 + lead2 + lag1 + lag2 >= 3
        ) AS wk
        WHERE {}_result.timestamp IN (wk.timestamp)
    """.format(ship, ship, ship)

    calc_interval = """
        SELECT wl.timestamp, wl.num_neighbours, wl.name, ((lead(timestamp) OVER (ORDER BY timestamp ASC)) - timestamp) AS interval, wl.geom, wl.pause
        FROM
            (SELECT name, timestamp, num_neighbours, geom, pause, lag(pause) OVER (ORDER BY timestamp ASC) AS prev_pause,
                lead(pause) OVER (ORDER BY timestamp ASC) AS next_pause
            FROM {}_result
            ORDER BY timestamp ASC) AS wl
        WHERE wl.pause IS DISTINCT FROM wl.next_pause
        ORDER BY name ASC, wl.timestamp ASC;
    """.format(ship)

    con.execute(drop_table)
    con.execute(create_table)
    con.execute(set_geom1)
    con.execute(set_geom2)
    con.execute(set_geom3)
    con.execute(create_index)
    con.execute(add_column1)
    con.execute(add_column2)
    con.execute(add_column3)
    con.execute(calc_neighbours)
    con.execute(set_pause1)
    con.execute(set_pause2)
    con.execute(set_pause3)

    df_res = pd.read_sql_query(calc_interval, con=con)

    df_res.to_csv(r'D:\Users\krob\Documents\AIS\Scripts\output_rws\interval_{}.csv'.format(ship))