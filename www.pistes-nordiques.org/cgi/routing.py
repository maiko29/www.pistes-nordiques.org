#!/usr/bin/env python

#import cgi
import sys, os, os.path
import math, random
import StringIO
from xml.sax import make_parser, handler
import xml


def application(environ,start_response):
    request = environ['QUERY_STRING']
    
    coord = request.split(',')
    #coord = req[:-1].split(',')
    
    # define the bbox where requesting the data
    minlat=float(coord[0].split(';')[0])
    minlon=float(coord[0].split(';')[1])
    maxlat=float(coord[0].split(';')[0])
    maxlon=float(coord[0].split(';')[1])
    
    for c in coord:
        if c :
            if (float(c.split(';')[0])<minlat):minlat=float(c.split(';')[0])
            if (float(c.split(';')[0])>maxlat):maxlat=float(c.split(';')[0])
            if (float(c.split(';')[1])<minlon):minlon=float(c.split(';')[1])
            if (float(c.split(';')[1])>maxlon):maxlon=float(c.split(';')[1])
    margin = 0.1
    randFilename = random.randrange(0, 100001, 2)
    dir = '/var/tmp/'
    #PIL_images_dir = 'images/' #XX
    filename = str(randFilename)+'.osm'

    os.popen("/home/website/src/osmosis-0.40.1/bin/osmosis \
    --read-pgsql host=\"localhost\" database=\"pistes-xapi\" user=\"xapi\" password=\"xapi\" \
    --dataset-bounding-box left="+str(minlon-margin)+" right="+str(maxlon+margin)+ " top="+str(maxlat+margin)+" bottom="+str(minlat-margin)+" completeWays=yes \
    --write-xml file="+dir+filename,'r')
    
    # Load data from the bbox
    data = LoadOsm(dir+filename)
    
    # Route between successive points send to the script:
    routeNodes = []
    routeWays = []
    for i in range(len(coord)-2):
        lon1 = float(coord[i].split(';')[1])
        lat1 = float(coord[i].split(';')[0])
        lon2 = float(coord[i+1].split(';')[1])
        lat2 = float(coord[i+1].split(';')[0])
        
        node1 = data.findNode(lat1, lon1)
        node2 = data.findNode(lat2, lon2)
        
        router = Router(data)
        result, route, nodes, ways= router.doRouteAsLL(node1, node2)
        
        routeNodes.append(nodes)
        routeWays.extend(ways)
        
        if (result == 'success'): continue
        else:
            
            wkt = result
            xml = '<?xml version="1.0" encoding="UTF-8" ?>\n  <route>\n'
            xml += '    <wkt>' + wkt + '\n    </wkt>\n'
            xml += '  </route>\n'
            status = '200 OK'
            response_body=xml
            response_headers = [('Content-Type', 'application/xml'),('Content-Length', str(len(response_body)))]
            start_response(status, response_headers)
            return [response_body]

    

    #create an ordered list by way id:
    #[[way,[nodes, node2],{tags}] , [way2,...]]
    #first :
    wayid = int(routeWays[1].split(',')[1])
    nodeid = int(routeWays[0].split(',')[0])
    try: tags = data.ways[wayid]['tags']
    except: tags = {}
    wayDict = [[wayid,[nodeid],tags]]
    
    for i in range(2,len(routeWays)):
        wayid = int(routeWays[i].split(',')[1])
        nodeid = int(routeWays[i-1].split(',')[0])
        try: tags = data.ways[wayid]['tags']
        except: tags = {}
        if (wayid != wayDict[-1][0]) & (wayid != 0):
            print wayid
            wayDict.append([wayid,[nodeid],tags])
        elif (wayDict[-1][1][-1] != nodeid):
            wayDict[-1][1].append(nodeid)
    # and last:
    wayDict[-1][1].append(int(routeWays[i].split(',')[0]))
    
    #extend the list with relations route=ski:
    #[[way,[nodes, node2],{tags},[[rel1, {tags}],[rel2, {tags}], ...] , [way2,...]]
    
    for way in wayDict:
        way.append([])
        for rel in data.relations:
            for tag in data.relations[rel]['tags']:
                if (tag == 'route'):
                    if ((data.relations[rel]['tags']['route'] == 'ski') or (data.relations[rel]['tags']['route'] == 'piste')):
                        if (way[0] in data.relations[rel]['n']):
                            way[3].append([rel,data.relations[rel]['tags']])
    print wayDict
      
    # keep only interesting tags
    interestingsKeys=['route', 'type', 'name' , 'color', 'website', \
    'colour', 'ref', 'operator', 'distance', 'length', \
    'piste:type', 'piste:grooming', 'piste:difficulty', 'piste:lit', \
    'piste:name', 'piste:status', 'piste:oneway', 'piste:abandoned']
    for way in wayDict:
        for key in way[2].keys():
            if key in interestingsKeys: pass
            else: way[2].pop(key)
        for i in range(len(way[3])):
                for key in way[3][i][1].keys():
                    if key in interestingsKeys: pass
                    else: way[3][i][1].pop(key)
            
            
    # concatenate similar ways
    outWayDict=[wayDict[0]]
    for i in range(1,len(wayDict)):
        way1=wayDict[i-1]
        way2=wayDict[i]
        flag= True
        if (way1[3] != way2[3]): # members of the same relation or not
            flag= False
        for key in way2[2].keys():
            try:
                if (way2[2][key] != way1[2][key]): flag= False
            except:
                pass
        if flag:
            outWayDict[-1][1].extend(way2[1]) #concatenate the nodes
        else:
            outWayDict.append(way2)

    # calculate length:
    for way in outWayDict:
        #print "way", way[0]
        length = 0
        for i in range (1,len(way[1])):
            lon1 = data.nodes[way[1][i]][1]
            lat1 = data.nodes[way[1][i]][0]
            lon2 = data.nodes[way[1][i-1]][1]
            lat2 = data.nodes[way[1][i-1]][0]
            length += linearDist(lat1, lon1, lat2, lon2)
            #print length
        way[2]['length']=str(length)
        #print "length",way[2]['length']

    # create the WKT LinseString:
    #wkt='LINESTRING('
    #for n in routeNodes:
        #wkt=wkt+str(data.nodes[int(n)][1])+ ' '+ str(data.nodes[int(n)][0]) +','
    #wkt=wkt[:-2]+')'
    
    # create the WKT MultilineString:
    wkt='MULTILINESTRING(('
    for line in routeNodes:
        for n in line:
            wkt=wkt+str(data.nodes[int(n)][1])+ ' '+ str(data.nodes[int(n)][0]) +','
        wkt=wkt[:-2]+'),('
    wkt=wkt[:-3]+'))'
    
    # create XML:
    xml = '<?xml version="1.0" encoding="UTF-8" ?>\n  <route>\n'
    xml += '    <wkt>' + wkt + '\n    </wkt>\n'
    xml += '    <route_topo>\n'
    
    for way in outWayDict:
        xml += '      <way id="'+ str(way[0]) +'">\n'
        for key in way[2]:
            xml += '        <tag k="'+ key.encode( "utf-8" ) +'">' \
                + way[2][key].encode( "utf-8" ) + '</tag>\n'
        for rel in way[3]:
            xml += '        <member_of id="'+ str(rel[0])+'">"\n'
            for rel_key in rel[1]:
                xml += '          <rel_tag k="'+ rel_key.encode( "utf-8" ) +'">' \
                    + rel[1][rel_key].encode( "utf-8" ) + '</rel_tag>\n'
            xml += '        </member_of>\n'
        xml += '      </way>\n'
    xml += '    </route_topo>\n'
    xml += '  </route>\n'
    
    status = '200 OK'
    response_body=xml
    response_headers = [('Content-Type', 'application/xml'),('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    return [response_body]
    
    

class Router:
    def __init__(self, data):
        self.data = data
    def distance(self,n1,n2):
        """Calculate distance between two nodes"""
        lat1 = self.data.nodes[n1][0]
        lon1 = self.data.nodes[n1][1]
        lat2 = self.data.nodes[n2][0]
        lon2 = self.data.nodes[n2][1]
        # TODO: projection issues
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        dist2 = dlat * dlat + dlon * dlon
        return(math.sqrt(dist2))
    def doRouteAsLL(self,start,end):
        result, nodes ,ways= self.doRoute(start,end)
        
        if(result != 'success'):
            return(result,[],[],[])
        pos = []
        for node in nodes:
            lat,lon = self.data.nodes[node]
            pos.append((lat,lon))
        return(result, pos, nodes, ways)
    def doRoute(self,start,end):
        """Do the routing"""
        self.searchEnd = end
        closed = [start]
        self.queue = []
        
        # Start by queueing all outbound links from the start node
        #blankQueueItem = {'end':-1,'distance':0,'nodes':[(str(start),0)]}
        blankQueueItem = { \
                        'end':-1,
                        'distance':0,
                        'nodes':str(start),
                        'ways':str(start)+',0'}
        try:
            for i, wayid in self.data.routing[start].items():
                self.addToQueue(start,i, blankQueueItem, wayid)
        except KeyError:
            return('no_such_node',[],[])
        
        # Limit for how long it will search
        count = 0
        while count < 10000:
            count = count + 1
            try:
                nextItem = self.queue.pop(0)
            except IndexError:
                print "Queue is empty: failed"
                return('no_route',[],[])
            x = nextItem['end']
            if x in closed:
                continue
            if x == end:
                # Found the end node - success
                #routeNodes = [int(i[0]) for i in nextItem['nodes']]
                routeNodes = [int(i) for i in nextItem['nodes'].split(",")]
                return('success', routeNodes, nextItem['ways'].split(";"))
            closed.append(x)
            try:
                for i, wayid in self.data.routing[x].items():
                    if not i in closed:
                        self.addToQueue(x,i,nextItem, wayid)
            except KeyError:
                pass
        else:
            return('gave_up',[],[])
    
    def addToQueue(self,start,end, queueSoFar, wayid):
        """Add another potential route to the queue"""
        
        # If already in queue
        for test in self.queue:
            if test['end'] == end:
                return
        distance = self.distance(start, end)
        #if(weight == 0):
            #return
        #distance = distance / weight
        
        # Create a hash for all the route's attributes
        distanceSoFar = queueSoFar['distance']
        #try: nodes = queueSoFar['nodes'].append((str(end),str(wayid)))
        #except: pdb.set_trace()
        nodes= queueSoFar['nodes'] + "," + str(end)
        ways= queueSoFar['ways']+ ";" +str(end)+ "," +str(wayid)
        queueItem = { \
            'distance': distanceSoFar + distance,
            'maxdistance': distanceSoFar + self.distance(end, self.searchEnd),
            'nodes': nodes,
            'ways': ways,
            'end': end}
        
        # Try to insert, keeping the queue ordered by decreasing worst-case distance
        count = 0
        for test in self.queue:
            if test['maxdistance'] > queueItem['maxdistance']:
                self.queue.insert(count,queueItem)
                break
            count = count + 1
        else:
            self.queue.append(queueItem)

def linearDist(lat1, lon1, lat2, lon2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = lon1*degrees_to_radians
    theta2 = lon2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( clamp(cos,-1,1)) # clamp will avoid rounding error that would lead cos outside of [-1,1] 'Math domain error'

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    
    return arc*6371 #return km
    
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    
    d = math.acos(math.sin(lat1)*math.sin(lat2) + \
                  math.cos(lat1)*math.cos(lat2) * \
                  math.cos(lon2-lon1)) * 6371 
    return d

#
def clamp(value, minvalue, maxvalue):
    return max(minvalue, min(value, maxvalue))
#
if __name__ == "__main__":
    handle("46.819861857936 6.3819670541344,46.827446755502 6.3980225909661,")#46.833474656204 6.4021853614751,")

#!/usr/bin/python
#----------------------------------------------------------------
# load OSM data file into memory
#
#------------------------------------------------------
# Usage: 
#     data = LoadOsm(filename)
# or:
#     loadOsm.py filename.osm
#------------------------------------------------------
# Copyright 2007, Oliver White
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.    If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------
# Changelog:
#    2007-11-04    OJW    Modified from pyroute.py
#    2007-11-05    OJW    Multiple forms of transport
#------------------------------------------------------


class LoadOsm(handler.ContentHandler):
    """Parse an OSM file looking for routing information, and do routing with it"""
    def __init__(self, filename, storeMap = 1):
        """Initialise an OSM-file parser"""
        self.routing = {}
        self.routeableNodes = {}
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.storeMap = storeMap
        
        if(filename == None):
            return
        self.loadOsm(filename)
        
    def loadOsm(self, filename):
        if(not os.path.exists(filename)):
            print "No such data file %s" % filename
            return
        try:
            parser = make_parser()
            parser.setContentHandler(self)
            parser.parse(filename)
        except xml.sax._exceptions.SAXParseException:
            print "Error loading %s" % filename
        
    def report(self):
        """Display some info about the loaded data"""
        report = "Loaded %d nodes,\n" % len(self.nodes.keys())
        report = report + "%d ways, and...\n" % len(self.ways)
        report = report + " %d routes\n" % ( \
            len(self.routing.keys()))
        return(report)
        
    def savebin(self,filename):
        self.newIDs = {}
        
        f = open(filename,"wb")
        f.write(pack('L',len(self.nodes.keys())))
        count = 0
        for id, n in self.nodes.items():
            self.newIDs[id] = count
            f.write(encodeLL(n[0],n[1]))
            count = count + 1
            
        errors = 0
        data = self.routing.items()
        f.write(pack('L', len(data)))
        for fr, destinations in data:
            try:
                f.write(pack('L', self.newIDs[fr]))
            except KeyError:
                f.write(pack('L', 0))
                errors = errors + 1
                continue
            f.write(pack('B', len(destinations.keys())))
            for to, weight in destinations.items():
                try:
                    f.write(pack('Lf', self.newIDs[to], weight))
                except KeyError:
                    f.write(pack('Lf', 0, 0))
                    errors = errors + 1
            
        print "%d key errors" % errors
        f.close()
        
    def loadbin(self,filename):
        f = open(filename,"rb")
        n = unpack('L', f.read(4))[0]
        print "%u nodes" % n
        id = 0
        for i in range(n):
            lat,lon = decodeLL(f.read(8))
            #print "%u: %f, %f" % (id,lat,lon)
            id = id + 1

        numLinks = 0
        numHubs = unpack('L', f.read(4))[0]
        print numHubs
        for hub in range(numHubs):
            fr = unpack('L', f.read(4))[0]
            numDest = unpack('B', f.read(1))[0]
            for dest in range(numDest):
                to,weight = unpack('Lf', f.read(8))
                numLinks = numLinks + 1
            #print fr, to, weight
        print "    \"\" (%u segments)" % (numLinks)

        f.close()

    def startElement(self, name, attrs):
        """Handle XML elements"""
        if name in('node','way','relation'):
            
            self.tags = {}
            self.waynodes = []
            self.relationmembers= []
            self.id = int(attrs.get('id'))
            if name == 'node':
                """Nodes need to be stored"""
                id = int(attrs.get('id'))
                lat = float(attrs.get('lat'))
                lon = float(attrs.get('lon'))
                self.nodes[id] = (lat,lon)
            #if name == 'way':
                #self.id = int(attrs.get('id'))
        elif name == 'nd':
            """Nodes within a way -- add them to a list, they can be stored later with storemap"""
            self.waynodes.append(int(attrs.get('ref')))
        elif name == 'member':
            """Ways within a relation -- add them to a list, they can be stored later with storemap"""
            self.relationmembers.append(int(attrs.get('ref')))
            print attrs.get('ref')
        elif name == 'tag':
            """Tags - store them in a hash"""
            k,v = (attrs.get('k'), attrs.get('v'))
            if not k in ('created_by'):
                self.tags[k] = v
    
    def endElement(self, name):
        """Handle ways in the OSM data"""
        if name == 'way':
            
            # Store routing information
            last = -1
            for i in self.waynodes:
                if last != -1:
                    weight = 1
                    self.addLink(last, i, self.id)
                    self.addLink(i, last, self.id)
                last = i
            
            # Store map information
            if(self.storeMap):
                wayType = self.WayType(self.tags)
                self.ways[self.id] = { \
                    't':wayType,
                    'n':self.waynodes,
                    'tags':self.tags}
        if name == 'relation':
            if(self.storeMap):
                self.relations[self.id] = { \
                    'n':self.relationmembers,
                    'tags':self.tags}
    
    def addLink(self,fr,to, wayid):
        """Add a routeable edge to the scenario"""
        self.routeablefrom(fr)
        try:
            if to in self.routing[fr].keys():
                return
            self.routing[fr][to] = wayid
        except KeyError:
            self.routing[fr] = {to: wayid}

    def WayType(self, tags):
        value = tags.get('piste:type', '')
        return value
        
    def routeablefrom(self,fr):
        self.routeableNodes[fr] = 1

    def findNode(self,lat,lon):
        """Find the nearest node to a point.
        Filters for nodes which have a route leading from them"""
        maxDist = 1000
        nodeFound = None
        for id in self.routeableNodes.keys():
            if id not in self.nodes:
                print "Ignoring undefined node %s" % id
                continue
            n = self.nodes[id]
            dlat = n[0] - lat
            dlon = n[1] - lon
            dist = dlat * dlat + dlon * dlon
            if(dist < maxDist):
                maxDist = dist
                nodeFound = id
        return(nodeFound)
        
# Parse the supplied OSM file
if __name__ == "__main__":
    print "Loading data..."
    data = LoadOsm(sys.argv[1], True)
    print data.report()
    print "Saving binary..."
    data.savebin("data/routing.bin")
    print "Loading binary..."
    data2 = LoadOsm(None, False)
    data2.loadbin("data/routing.bin")
    print "Done"

Weightings = { \
  'motorway': {'car':10},
  'trunk':    {'car':10, 'cycle':0.05},
  'primary':  {'cycle': 0.3, 'car':2, 'foot':1, 'horse':0.1},
  'secondary': {'cycle': 1, 'car':1.5, 'foot':1, 'horse':0.2},
  'tertiary': {'cycle': 1, 'car':1, 'foot':1, 'horse':0.3},
  'unclassified': {'cycle': 1, 'car':1, 'foot':1, 'horse':1},
  'minor': {'cycle': 1, 'car':1, 'foot':1, 'horse':1},
  'cycleway': {'cycle': 3, 'foot':0.2},
  'residential': {'cycle': 3, 'car':0.7, 'foot':1, 'horse':1},
  'track': {'cycle': 1, 'car':1, 'foot':1, 'horse':1, 'mtb':3},
  'service': {'cycle': 1, 'car':1, 'foot':1, 'horse':1},
  'bridleway': {'cycle': 0.8, 'foot':1, 'horse':10, 'mtb':3},
  'footway': {'cycle': 0.2, 'foot':1},
  'steps': {'foot':1, 'cycle':0.3},
  'rail':{'train':1},
  'light_rail':{'train':1},
  'subway':{'train':1},
  'nordic':{'ski':1}
  }

def getWeight(transport, wayType):
  try:
    return(Weightings[wayType][transport])
  except KeyError:
    # Default: if no weighting is defined, then assume it can't be routed
    return(0)


def encodeLL(lat,lon):
  pLat = (lat + 90.0) / 180.0 
  pLon = (lon + 180.0) / 360.0 
  iLat = encodeP(pLat)
  iLon = encodeP(pLon)
  return(pack("II", iLat, iLon))
  
def encodeP(p):
  i = int(p * 4294967296.0)
  return(i)
  

def decodeLL(data):
  iLat,iLon = unpack("II", data)
  pLat = decodeP(iLat)
  pLon = decodeP(iLon)
  lat = pLat * 180.0 - 90.0
  lon = pLon * 360.0 - 180.0
  return(lat,lon)
  
def decodeP(i):
  p = float(i) / 4294967296.0
  return(p)
  
