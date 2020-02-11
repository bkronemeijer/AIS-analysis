######################################################################
# each raster in a directory is merged into one raster that 
# displays the waterway occupancy
######################################################################

import os
import functools
import numpy as np
from osgeo import gdal, osr, ogr

def add_rasters(base_path=r"D:\Users\krob\Documents\AIS\Scripts\output_rws\track_tiff\individual_rasters"):
    for counter, directory in enumerate(os.listdir(base_path)):
        
        # settings for output raster layer
        output = r"D:\Users\krob\Documents\AIS\Scripts\output_rws\track_tiff\total_rasters\{}_wgs84.tif".format(directory)
        pixel_size = 0.025

        extent_shp = ogr.Open(r"D:\Users\krob\Documents\AIS\extent.shp")
        extent_layer = extent_shp.GetLayer()
        x_min, x_max, y_min, y_max = extent_layer.GetExtent()

        x_res = int((x_max - x_min) / pixel_size)
        y_res = int((y_max - y_min) / pixel_size)

        raster_total_array = []

        # set spatial reference system
        srs = osr.SpatialReference()
        # srs.ImportFromEPSG(28992)
        srs.ImportFromEPSG(4326)
        dest_wkt = srs.ExportToWkt()

        for counter, filen in enumerate(os.listdir(r'{}\{}'.format(base_path, directory))):
            # open raster file
            workfile = r'{}\{}\{}'.format(base_path, directory, filen)
            raster = gdal.Open(workfile, gdal.GA_Update)

            # set spatial reference
            raster.SetProjection(dest_wkt)

            # send raster as np array to raster_total_array
            raster_array = raster.ReadAsArray()
            raster_total_array.append(raster_array)

            # raster = None

        concat_raster = functools.reduce(lambda a, b: np.add(a, b), raster_total_array)

        target_ds = gdal.GetDriverByName('GTiff').Create(output, x_res, y_res, 1, gdal.GDT_Byte)
        target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
        target_ds.SetProjection(dest_wkt)

        target_ds.GetRasterBand(1).WriteArray(concat_raster)

        target_ds.FlushCache()
