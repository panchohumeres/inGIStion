#archivo para probar requerir un solo tile, en este ejemplo un tile geojson
#en este ejemplo es con un archivo de configuracion incluido en la carpeta confs
#documentacion de las clases y funciones python de TileStache en http://tilestache.org/doc/TileStache.html y en la seccion "in code" en http://tilestache.org/doc/

from ModestMaps import Core
import TileStache
from slippy_geo_functions import deg2num #import funcion for converting lat,long to slippy maps coordinates (module script "slippy_geo_functions.py" must be in same directory)
#la linea anterior se puede comentar si es que no se va a usar esa libreria


#path='tilestache_test_man_liv_tweets_nov_2013_shp.cfg'
path='../confs/tilestache_test_tengo_slant_shp.cfg' #archivo de configuracion tilestache
layer='tengo' #layer especifica dentro del archivo de configuracion para requerir
zoom=15
lat=-33.34092334000001
lon=-70.51617780999999

x,y=deg2num(lat,lon,zoom) #convert to slippy maps coords
#zoom,x,y=0,0,0 #si se quiere definir las coordenadas slippy maps directamente comentar la linea anterior y descomentar esta

conf=TileStache.parseConfigfile(path) #escanear el archivo de configuracion
ly=conf.layers[layer] #sacar el objeto relativo a una layer en especifico
coord=Core.Coordinate(zoom,x,y) #crear un objeto coord de Modestmaps (el formato slippy maps para requerir el tile, en este ejemplo es 0/0/0 o sea todo, pero puede ser cualquier otro)
TileStache.getTile(ly,coord,'geojson') #llamar el tile e imprimirlo en consola (especificar el formato de salida para el tile)
#tile=TileStache.getTile(man,coord,'geojson') #llamar el tile y guardarlo en una variable