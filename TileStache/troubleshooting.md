# TROUBLESHOOTING #

Cualquier reporte de bugs, problemas, o malinterpretaciones de la configuracion de un servidor de mapas de TileStache.

### Archivos CONF ###
Es recomendable editarlos como json para no equivocarse con los corchetes ("{}")

* ".json" no es una extension valida para incluir en el proveedor "Vector", es un erro de la documentacion http://tilestache.org/doc/TileStache.Vector.html (no es aceptable .json, esta mal)
*en el proveedor "Vector" los shapefiles o gejson (source) que estan en "google mercator", o "web mercator" (EPSG:3857 a.k.a.) deben ser convertidos con parametro "projected" o tilestache los va a interpretar como coordenadas lat,long (estas proyecciones no estan en la forma lat, long)------>"projected":true (ojo, "true" sin letra capital)


### Visualizacion via browser ###
* Acordarse que el dominio para probar en localhost es "localhost:8080" (no olvidarse de incluir el puerto)------>esto para el caso de testeo con tilestache-servery.py