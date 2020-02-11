######################################################################
# postgres database: ais_test
# postgres table: ships

# this script selects instances based on customisable properties 
# from a psql database and generates a frequency map in raster format
######################################################################

import os
import csv
import getpass
import pandas as pd
from sqlalchemy import create_engine, MetaData
from osgeo import gdal, ogr, osr
from shapely import wkb, wkt
from add_rasters import add_rasters

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
filen = '10JuneAllShips'
begindates = ['2019-06-09 04:00:00' , '2019-06-09 06:00:00', '2019-06-09 08:00:00', '2019-06-09 10:00:00', '2019-06-09 12:00:00', '2019-06-09 14:00:00', '2019-06-09 16:00:00', '2019-06-09 18:00:00', '2019-06-09 20:00:00', '2019-06-09 22:00:00']
enddates = ['2019-06-09 06:00:00', '2019-06-09 08:00:00', '2019-06-09 10:00:00', '2019-06-09 12:00:00', '2019-06-09 14:00:00', '2019-06-09 16:00:00', '2019-06-09 18:00:00', '2019-06-09 20:00:00', '2019-06-09 22:00:00', '2019-06-10 00:00:00']
vesseltype = '*'
hazardouscargo = '*'

# # uncomment lines 38 - 46 in order to extract query-based pandas dataframe from psql database

# for index, row in df.iterrows():
#     try:
#         shape = wkt.loads(row['geom'])
#         df['shape'] = shape
#     except:
#         shape = 'point'
#         df['shape'] = shape

# df.to_csv(r'D:\Users\krob\Documents\AIS\Scripts\output_rws\TEST_8_1.csv')

# # create raster layer
for first_index, begindate in enumerate(begindates):
    enddate = enddates[first_index]

    total_query = """
        SELECT 
            ships.name, 
            ST_AsText(ST_MakeLine(ships.geom ORDER BY timestamp)) As geom
        FROM ships
        WHERE ST_Intersects(ST_SetSRID(
                ST_MakeBox2D(St_MakePoint(5.710553, 52.844946), ST_MakePoint(6.9244598, 53.3310272)), 4326), ships.geom)
            AND timestamp BETWEEN '{}' AND '{}'
        GROUP BY name
    """.format(begindate, enddate)

    df = pd.read_sql_query(total_query, con=con)

    if not os.path.exists('D:\\Users\\krob\\Documents\\AIS\\Scripts\\output_rws\\track_tiff\\individual_rasters\\{}'.format(first_index)):
        os.mkdir("D:\\Users\\krob\\Documents\\AIS\\Scripts\\output_rws\\track_tiff\\individual_rasters\\{}".format(first_index))

    for second_index, row in df.iterrows():
        # set spatial reference system
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        sr_wkt = srs.ExportToWkt()

        # create memory raster
        output = "D:\\Users\\krob\\Documents\\AIS\\Scripts\\output_rws\\track_tiff\\individual_rasters\\{}\\{}_0025_individualTest.tif".format(first_index, second_index)
        pixel_size = 0.025
        extent_shp = ogr.Open(r"D:\Users\krob\Documents\AIS\extent.shp")
        extent_layer = extent_shp.GetLayer()
        x_min, x_max, y_min, y_max = extent_layer.GetExtent()

        x_res = int((x_max - x_min) / pixel_size)
        y_res = int((y_max - y_min) / pixel_size)

        target_ds = gdal.GetDriverByName('GTiff').Create( output, x_res, y_res, 1, gdal.GDT_Byte )
        target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
        target_ds.SetProjection( sr_wkt )

        # create a memory layer to rasterize from
        rast_ogr_ds = ogr.GetDriverByName('Memory').CreateDataSource( 'wrk' )
        rast_mem_lyr = rast_ogr_ds.CreateLayer('line', srs=srs)

        shp = row['geom']
        feat = ogr.Feature( rast_mem_lyr.GetLayerDefn() )
        feat.SetGeometry( ogr.Geometry(wkt = shp) )
        rast_mem_lyr.CreateFeature( feat )

        # gdal.RasterizeLayer(target_ds, [1], rast_mem_lyr, burn_values=[1], options=['noData=0', 'MERGE_ALG=ADD', 'ALL_TOUCHED=TRUE'])
        temp_rast = gdal.RasterizeLayer(target_ds, [1], rast_mem_lyr, burn_values=[1], options=['noData=0', 'ALL_TOUCHED=TRUE'])

add_rasters("D:\\Users\\krob\\Documents\\AIS\\Scripts\\output_rws\\track_tiff\\individual_rasters")