# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Repositorio personal (F.Humeres) para asegurar instalacion exitosa de TileStache en varios sistemas
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### Testeo ###
* Para probar el servidor (de formar autocontenida), sin configurar apache, correr el script ./scripts/tilestache-server.py en la carpeta TileStache.
* Al correr el script, se puede verificar que funciona en el browser con el dominio localhost:8080
* Para probar algun archivo de configuracion especifico, correr ./scripts/tilestache-server.py -c ruta_al_archivo_conf, (la ruta puede ser relativa o asboluta), y verificar con el dominio localhost:8080/nombre_de_layer/preview.html o localhost:8080/nombre_de_layer/x/y/z/.extension (por ejemplo .png, .geojson, etc.).
* Para testear una capa especifica en algun archivo de configuracion espeficio, es preferible incluir la directiva "preview" en el archivo de conifugracion (para configurar donde centrar el mapa, el nivel de zoom, etc.) y usar el dominio que utiliza preview.html
*Un ejemplo de esa directiva es (ver los archivos de la carpeta Confs tambien):
      "preview": 

        {
        "lat": 53.483959,
        "lon": -2.244644,
        "zoom": 15,
        "ext": "geojson"}
*En la carpeta python se incluyen scripts y guias para hacer debugging o testeo a traves de python.
*En la carpeta python tambien se incluyen funciones para operaciones geo--->slippy maps (p.ej. convertir lat,long a esquema slippy maps /z/x/y)

### Carpetas ###

* TilesTache/
Source Code de TileStache obtenido desde: git clone https://github.com/TileStache/TileStache.git TileStache
* Confs/
Ejemplos de archivos de configuracion .conf (o .json) de TileStache
* js/
Archivos Javascript
* HTML/
Archivos HTML para probar despliegue de tiles

### Debugging ###
En el archivo "troubleshooting.md" se incluye lista de bugs, problemas malasinterpretaciones encontradas en la configuracion de un servidor de mapas TileStache.


### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact