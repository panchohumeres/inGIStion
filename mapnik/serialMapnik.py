import mapnik
from pandas import DataFrame
import os
import sys
import glob
import xml.etree.ElementTree as ET

path=sys.argv[1] #read folder with files from argument (from command line)

paths=[]

stylePath=sys.argv[2] #path to mapnik xml styles for getting generic style
kwargs = dict(x.split('=', 1) for x in sys.argv[3:]) #make dictionary from variable number of arguments passed to script (after files directory)
args={'minzoom':'0','maxzoom':'14','dir':None} #default arguments for converter function

#styleName=stylePath.rsplit('/',1)[-1].rsplit('.',1)[0] #this is the name of the desired style in the mapnik xml file
#styleName=sys.argv[3]
outputPath=stylePath.rsplit('/',1)[-1].rsplit('.',1)[0] #output rebranded mapnik xml to save
for key, value in kwargs.iteritems(): 
	if key=='minzoom': #if header is specified change default (zero-->0)
		args['minzoom']=value

	if key=='maxzoom':
		 args['maxzoom']=value

	if key=='dir': #if output dir is specified
		args['dir']=value

		if args['dir'][len(args['dir'])-1]=='/': #if last character of path is '/'
			args.rsplit('/',1)[0]

		if not os.path.exists(args['dir']): #if folder doesnt exist create it
			os.makedirs(args['dir'])



subdirectories = os.listdir(path)



for n in range(0,len(subdirectories)):
	subdirectories[n]=path+'/'+subdirectories[n] #complete the subfolder paths with master folder

for s in subdirectories:
	for filename in glob.glob(os.path.join(s, '*.shp')): paths.append(filename) #get list of shapefiles


tree = ET.parse(stylePath) #load mapnik xml to be copied styles from
root = tree.getroot()


for path in paths:

	mapnikPath=path.rsplit('/',1)[-1].rsplit('.',1)[0] #keep just name of the shapefiles, without extension neither path to file (the name between the las t'/' and '.'')
	

	directory=path.rsplit('/',1)[0]+'/'
	

	#xmlstr = ET.tostring(root, encoding='utf8', method='xml')


	ds= mapnik.Shapefile(file=path)

	bounding=tuple(float(x) for x in ds.envelope())
	center=str(bounding[0]+(bounding[0]-bounding[2])/2)+','+str(bounding[1]-(bounding[1]-bounding[3])/2)



	bounding=''.join([str(x)+',' for x in ds.envelope()]).rstrip(',') #make bounding box



	style=root.find('Style') #change style name
	style.attrib['name']=mapnikPath+'Style'

	layer=root.find('Layer') 
	layer.attrib['name'] #change name of layer
	layer.find('StyleName').text=mapnikPath+'Style' #change name of style (in the layer)

	absPath=os.path.abspath(path) #use absolute path for shapefile datasource

	datasource=layer.find('Datasource')#change datasource

	for i in datasource:
		if i.attrib['name']=='file':
			i.text=absPath



	params=root.find('Parameters') #add bounding box
	for i in params:
		if i.attrib['name']=='bounds':
			i.text=bounding

		if i.attrib['name']=='center':
			i.text=center

		if i.attrib['name']=='id':
			i.text=mapnikPath

		if i.attrib['name']=='name':
			i.text=mapnikPath

		if i.attrib['name']=='tilejson':
			i.text='2.0.0'

		if i.attrib['name']=='scheme':
			i.text='xyz'

		if i.attrib['name']=='minzoom':
			i.text=args['minzoom']

		if i.attrib['name']=='maxzoom':
			i.text=args['maxzoom']

	if args['dir']==None: #if no dir was provided, use default
		mapnikPath=directory+mapnikPath #save mapnik next to shapefiles
		mapnikPath=mapnikPath+'.xml'

	else:
		if args['dir'][len(args['dir'])-1]=='/':
			mapnikPath=args['dir']+mapnikPath+'.xml'
		else:
			mapnikPath=args['dir']+'/'+mapnikPath+'.xml'


	tree.write(mapnikPath)



