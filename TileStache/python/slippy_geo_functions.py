# -*- coding: utf-8 -*-
import math
#module that contains python functions for geographic conversions and operations for slippy maps protocol

# *************functions for slippy map geographic conversions in python from open street map************************
#at: http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers_2

#   Tiles are 256 × 256 pixel PNG files
#    Each zoom level is a directory, each column is a subdirectory, and each tile in that column is a file
#    Filename(url) format is /zoom/x/y.png
#The slippy map expects tiles to be served up at URLs following this scheme, so all tile server URLs look pretty similar. 

#La,Long to tile number
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)


#Tile numbers to lon./lat.
def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

# *************functions for slippy map geographic conversions in python from open street map********************