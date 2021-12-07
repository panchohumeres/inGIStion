#!/usr/bin/env python
from math import pi,cos,sin,log,exp,atan
from subprocess import call
import sys, os
from Queue import Queue
from pandas import DataFrame
import xml.etree.ElementTree as ET
import multiprocessing
import threading
import glob
import json
import os.path
#try:
#    import mapnik2 as mapnik
#except:
#    import mapnik

import mapnik

DEG_TO_RAD = pi/180
RAD_TO_DEG = 180/pi

# Default number of rendering threads to spawn, should be roughly equal to number of CPU cores available
#NUM_THREADS = 4
NUM_THREADS =multiprocessing.cpu_count()


def minmax (a,b,c):
    a = max(a,b)
    a = min(a,c)
    return a

class GoogleProjection:
    def __init__(self,levels=18):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0,levels):
            e = c/2;
            self.Bc.append(c/360.0)
            self.Cc.append(c/(2 * pi))
            self.zc.append((e,e))
            self.Ac.append(c)
            c *= 2
                
    def fromLLtoPixel(self,ll,zoom):
         d = self.zc[zoom]
         e = round(d[0] + ll[0] * self.Bc[zoom])
         f = minmax(sin(DEG_TO_RAD * ll[1]),-0.9999,0.9999)
         g = round(d[1] + 0.5*log((1+f)/(1-f))*-self.Cc[zoom])
         return (e,g)
     
    def fromPixelToLL(self,px,zoom):
         e = self.zc[zoom]
         f = (px[0] - e[0])/self.Bc[zoom]
         g = (px[1] - e[1])/-self.Cc[zoom]
         h = RAD_TO_DEG * ( 2 * atan(exp(g)) - 0.5 * pi)
         return (f,h)



class RenderThread:
    def __init__(self, tile_dir, mapfile, q, printLock, maxZoom):
        self.tile_dir = tile_dir
        self.q = q
        self.m = mapnik.Map(256, 256)
        self.printLock = printLock
        # Load style XML
        mapnik.load_map(self.m, mapfile, True)
        # Obtain <Map> projection
        self.prj = mapnik.Projection(self.m.srs)
        # Projects between tile pixel co-ordinates and LatLong (EPSG:4326)
        self.tileproj = GoogleProjection(maxZoom+1)


    def render_tile(self, tile_uri, x, y, z):

        # Calculate pixel positions of bottom-left & top-right
        p0 = (x * 256, (y + 1) * 256)
        p1 = ((x + 1) * 256, y * 256)

        # Convert to LatLong (EPSG:4326)
        l0 = self.tileproj.fromPixelToLL(p0, z);
        l1 = self.tileproj.fromPixelToLL(p1, z);

        # Convert to map projection (e.g. mercator co-ords EPSG:900913)
        c0 = self.prj.forward(mapnik.Coord(l0[0],l0[1]))
        c1 = self.prj.forward(mapnik.Coord(l1[0],l1[1]))

        # Bounding box for the tile
        if hasattr(mapnik,'mapnik_version') and mapnik.mapnik_version() >= 800:
            bbox = mapnik.Box2d(c0.x,c0.y, c1.x,c1.y)
        else:
            bbox = mapnik.Envelope(c0.x,c0.y, c1.x,c1.y)
        render_size = 256
        self.m.resize(render_size, render_size)
        self.m.zoom_to_box(bbox)
        if(self.m.buffer_size < 128):
            self.m.buffer_size = 128

        # Render image with default Agg renderer
        im = mapnik.Image(render_size, render_size)
        mapnik.render(self.m, im)
        im.save(tile_uri, 'png256')


    def loop(self):
        while True:
            #Fetch a tile from the queue and render it
            r = self.q.get()
            if (r == None):
                self.q.task_done()
                break
            else:
                (name, tile_uri, x, y, z) = r

            exists= ""
            if os.path.isfile(tile_uri):
                exists= "exists"
            else:
                self.render_tile(tile_uri, x, y, z)
            bytes=os.stat(tile_uri)[6]
            empty= ''
            if bytes == 103:
                empty = " Empty Tile "
            self.printLock.acquire()
            print name, ":", z, x, y, exists, empty
            self.printLock.release()
            self.q.task_done()



def render_tiles(bbox, mapfile, tile_dir, minZoom=1,maxZoom=18, name="unknown", num_threads=NUM_THREADS, tms_scheme=False):
    print "render_tiles(",bbox, mapfile, tile_dir, minZoom,maxZoom, name,")"

    # Launch rendering threads
    queue = Queue(32)
    printLock = threading.Lock()
    renderers = {}
    for i in range(num_threads):
        renderer = RenderThread(tile_dir, mapfile, queue, printLock, maxZoom)
        render_thread = threading.Thread(target=renderer.loop)
        render_thread.start()
        #print "Started render thread %s" % render_thread.getName()
        renderers[i] = render_thread

    if not os.path.isdir(tile_dir):
         os.mkdir(tile_dir)

    gprj = GoogleProjection(maxZoom+1) 

    ll0 = (bbox[0],bbox[3])
    ll1 = (bbox[2],bbox[1])

    for z in range(minZoom,maxZoom + 1):
        px0 = gprj.fromLLtoPixel(ll0,z)
        px1 = gprj.fromLLtoPixel(ll1,z)

        # check if we have directories in place
        zoom = "%s" % z
        if not os.path.isdir(tile_dir + zoom):
            os.mkdir(tile_dir + zoom)
        for x in range(int(px0[0]/256.0),int(px1[0]/256.0)+1):
            # Validate x co-ordinate
            if (x < 0) or (x >= 2**z):
                continue
            # check if we have directories in place
            str_x = "%s" % x
            if not os.path.isdir(tile_dir + zoom + '/' + str_x):
                os.mkdir(tile_dir + zoom + '/' + str_x)
            for y in range(int(px0[1]/256.0),int(px1[1]/256.0)+1):
                # Validate x co-ordinate
                if (y < 0) or (y >= 2**z):
                    continue
                # flip y to match OSGEO TMS spec
                if tms_scheme:
                    str_y = "%s" % ((2**z-1) - y)
                else:
                    str_y = "%s" % y
                tile_uri = tile_dir + zoom + '/' + str_x + '/' + str_y + '.png'
                # Submit tile to be rendered into the queue
                t = (name, tile_uri, x, y, z)
                try:
                    queue.put(t)
                except KeyboardInterrupt:
                    raise SystemExit("Ctrl-c detected, exiting...")

    # Signal render threads to exit by sending empty request to queue
    for i in range(num_threads):
        queue.put(None)
    # wait for pending rendering jobs to complete
    queue.join()
    for i in range(num_threads):
        renderers[i].join()



if __name__ == "__main__":

    path=sys.argv[1] #first argument, either mapnik xml file or directory of files
    tileDir=sys.argv[2]
    kwargs = dict(x.split('=', 1) for x in sys.argv[3:]) #make dictionary from variable number of arguments passed to script (after files directory)
    args={'minzoom':None,'maxzoom':None} #default arguments for converter function

    paths=[]

    for key, value in kwargs.iteritems(): 
        if key=='minzoom':
            args['minzoom']=value
        if key=='maxzoom':
         args['maxzoom']=value
         

    split=path.rsplit('.')

    if split[len(split)-1]=='xml': paths.append(path)

    if '/' in split[len(split)-1]: #if path is making reference to a directory
        if path[len(path)-1]!='/': #if '/' is not included as last characther in the path
            path=path+'/'
        for filename in glob.glob(os.path.join(path, '*.xml')): paths.append(filename) #get list of mapnik xml files

    else:
        print 'not an xml file nor directory, quitting script'
        sys.exit()



    #minZoom=int(sys.argv[3])
    #maxZoom=int(sys.argv[4])
    target=len(paths)
    count=1

    for mapfile in paths: #loop over list of mapnik files

        tile_dir=tileDir #initialize internal variable of folder for tiles, with copy from one provided in script parameters

        outputPath=[] #extra output path to use in case of multiple files

        print 'processing file: '+mapfile+' number: '+str(count)+' out of '+str(target)+' files'
        tree = ET.parse(mapfile) #read mapnik xml to find bounding box parameters
        root = tree.getroot()
        params=root.find('Parameters')

        bbox=[] 
        for i in params:
            if i.attrib['name']=='bounds':
                bbox=[float(n) for n in i.text.split(',')]

            if i.attrib['name']=='minzoom' and args['minzoom']==None: #if zoom is specified in mapfile
                args['minzoom']==i.text
            if i.attrib['name']=='maxzoom' and args['maxzoom']==None:
                args['maxzoom']==i.text

        if args['minzoom']==None: args['minzoom']=0 #if zooms were not specified in file, use defaults
        if args['maxzoom']==None: args['maxzoom']=14

        bbox=tuple(bbox) #make tuple of bounding box

        layer=root.find('Layer') 
        ds=layer.find('Datasource')#find datasource
        for i in ds:
            if i.attrib['name']=='file':
                datasource=i.text #path to datasource shapefile

        datasourcePATH=datasource.rsplit('/',1)[0] #path to datasource (without the file)
        shapeNAME=datasource.rsplit('/',1)[1].rsplit('.',1)[0] #name (just the name, without extension) of the shapefile
        

        if target>1: #create folder for output tiles (which will contain other layer's subfolders with tiles)
            if tile_dir[len(tile_dir)-1]=='/': #if las '/' character was included in path
                tile_dir=tile_dir+shapeNAME+'/' #name subfolder according to name of shapefile
            else:
                tile_dir=tile_dir+'/'+shapeNAME+'/' #name subfolder according to name of shapefile
            if not os.path.exists(tile_dir):
                os.makedirs(tile_dir)

        metadataFiles=[]

        for filename in glob.glob(os.path.join(datasourcePATH, '*metadata.json')): metadataFiles.append(filename)
        
        if len(metadataFiles)>0: #write to json metadata if exists (add bounding box parameters)
            for mf in metadataFiles:
                if shapeNAME in mf.rsplit('/',1)[1]: #IF THE NAME OF THE SHAPEFILE IS IN THE FILENAME (without the path)
                    with open(mf) as data_file:
                        metaData = json.load(data_file)
                        metaData['bounds']=[x for x in bbox] #add the extents
                        with open(tile_dir+shapeNAME+'_metadata.json', 'w') as fp: json.dump(metaData,fp)

        if not os.path.isfile(tile_dir+shapeNAME+'_metadata.json'): #if file didn't exist, create it    
            metaData={} #create json with bounding box
            metaData['bounds']=[x for x in bbox]
            with open(tile_dir+shapeNAME+'_metadata.json', 'w') as fp: json.dump(metaData,fp) #create bounding box json
        






        render_tiles(bbox, mapfile, tile_dir, int(args['minzoom']), int(args['maxzoom']))

        count+=1
    
    #env_file=mapfile.rsplit('.',1)[0] #take file styles extension
    #env_file=env_file+'_ext.csv' #add the extents extension for reading envelope file

    #env=DataFrame.from_csv(env_file)

    #bbox=(env.ix['lon_1',0],env.ix['lat_2',0],env.ix['lon_2',0],env.ix['lat_1',0])

    #bbox=(11.4,48.07, 11.7,48.22)

    #home = os.environ['HOME']
    #try:
    
    #    mapfile = os.environ['MAPNIK_MAP_FILE']
    #except KeyError:
    #    mapfile = home + "/svn.openstreetmap.org/applications/rendering/mapnik/osm-local.xml"
    #try:
    #    tile_dir = os.environ['MAPNIK_TILE_DIR']
    #except KeyError:
    #    tile_dir = home + "/osm/tiles/"

    #if not tile_dir.endswith('/'):
     #   tile_dir = tile_dir + '/'

    #-------------------------------------------------------------------------
    #
    # Change the following for different bounding boxes and zoom levels
    #
    # Start with an overview
    # World
    #bbox = (-180.0,-90.0, 180.0,90.0)

    #render_tiles(bbox, mapfile, tile_dir, 0, 5, "World")

    #minZoom = 10
    #maxZoom = 16
    #bbox = (-2, 50.0,1.0,52.0)
    #render_tiles(bbox, mapfile, tile_dir, minZoom, maxZoom)

    # Muenchen
   # bbox = (11.4,48.07, 11.7,48.22)
    #render_tiles(bbox, mapfile, tile_dir, 1, 12 , "Muenchen")

    # Muenchen+
    #bbox = (11.3,48.01, 12.15,48.44)
    #render_tiles(bbox, mapfile, tile_dir, 7, 12 , "Muenchen+")

    # Muenchen++
    #bbox = (10.92,47.7, 12.24,48.61)
    #render_tiles(bbox, mapfile, tile_dir, 7, 12 , "Muenchen++")

    # Nuernberg
    #bbox=(10.903198,49.560441,49.633534,11.038085)
    #render_tiles(bbox, mapfile, tile_dir, 10, 16, "Nuernberg")

    # Karlsruhe
    #bbox=(8.179113,48.933617,8.489252,49.081707)
    #render_tiles(bbox, mapfile, tile_dir, 10, 16, "Karlsruhe")

    # Karlsruhe+
    #bbox = (8.3,48.95,8.5,49.05)
    #render_tiles(bbox, mapfile, tile_dir, 1, 16, "Karlsruhe+")

    # Augsburg
    #bbox = (8.3,48.95,8.5,49.05)
    #render_tiles(bbox, mapfile, tile_dir, 1, 16, "Augsburg")

    # Augsburg+
    #bbox=(10.773251,48.369594,10.883834,48.438577)
    #render_tiles(bbox, mapfile, tile_dir, 10, 14, "Augsburg+")

    # Europe+
    #bbox = (1.0,10.0, 20.6,50.0)
    #render_tiles(bbox, mapfile, tile_dir, 1, 11 , "Europe+")
