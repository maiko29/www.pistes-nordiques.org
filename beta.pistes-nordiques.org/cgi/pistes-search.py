#!/usr/bin/python
#
# 
#

import psycopg2
import pdb
import sys, os
from lxml import etree
import json
import cgi

def application(environ,start_response):
	request = environ['QUERY_STRING']
	name=''
	point=''
	radius=''
	if request.find('name=') !=-1:
		name=request.split('name=')[1]
		if name.find('&'): name=name.split('&')[0]
	if request.find('point=') !=-1:
		point=request.split('point=')[1]
		if point.find('&'): point=point.split('&')[0]
	if request.find('radius=') !=-1:
		radius=request.split('radius=')[1]
		if radius.find('&'): radius=radius.split('&')[0]
	
	sites, entrances, routes, ways = query_ids(name,point,radius)
	response={}
	response['sites']= query_sites(sites)
	response['routes']= query_routes(routes)
	response['pistes']= query_ways(ways)
	response['aerialways']= query_aerialways(ways)
	response_body=json.dumps(response)
	status = '200 OK'
	response_headers = [('Content-Type', 'application/json'),('Content-Length', str(len(response_body)))]
	
	start_response(status, response_headers)
	return [response_body]
	
def query_ids(name='', point='', radius=''):
	con = psycopg2.connect("dbname=pistes-mapnik user=mapnik")
	cur = con.cursor()
	
	sites_ids=[]
	entrances_ids=[]
	routes_ids=[]
	ways_ids=[]
	
	# Query db, looking for 'name'
	if name != '':
		name=name.replace(' ','&').replace('%20','&')
		
		cur.execute("select osm_id from planet_osm_point where to_tsvector(site_name) @@ to_tsquery('%s');"\
			%(name))
		ids=cur.fetchall()
		for i in ids:
			idx=long(i[0])
			if idx < 0: sites_ids.append(str(idx))
			else: entrances_ids.append(str(idx))
			
		cur.execute("select osm_id from planet_osm_line where to_tsvector(COALESCE(route_name,'')||' '||COALESCE(name,'')||' '||COALESCE(\"piste:name\",'')) @@ to_tsquery('%s');"\
			%(name))
		ids=cur.fetchall()
		for i in ids:
			idx=long(i[0])
			if idx < 0: routes_ids.append(str(idx))
			else: ways_ids.append(str(idx))
		
	if point != '' and radius != '':
		radius=float(radius)*1000
		if radius > 500000: radius = 500000
		cur.execute("select osm_id from planet_osm_point where ST_DWithin(ST_Transform(ST_SetSRID(ST_MakePoint(%s),4326),900913), way, %s);"\
		%(point, str(radius)))
		ids=cur.fetchall()
		for i in ids:
			idx=long(i[0])
			if idx < 0: sites_ids.append(str(idx))
			else: entrances_ids.append(str(idx))
		
		cur.execute("select osm_id from planet_osm_line where ST_DWithin(ST_Transform(ST_SetSRID(ST_MakePoint(%s),4326),900913), way, %s);"\
		%(point, str(radius)))
		ids=cur.fetchall()
		for i in ids:
			idx=long(i[0])
			if idx < 0: routes_ids.append(str(idx))
			else: ways_ids.append(str(idx))
	con.close()
	return sites_ids, entrances_ids, routes_ids, ways_ids
	
	
def query_sites(sites_ids):
	con = psycopg2.connect("dbname=pistes-mapnik user=mapnik")
	cur = con.cursor()
	sites={}
	for idx in sites_ids:
		cur.execute("select site_name, \"piste:type\", ST_AsLatLonText(ST_Transform(way,4326), 'D.DDDDD') from planet_osm_point where osm_id = %s and \"piste:type\" is not null;"\
		%(idx))
		resp=cur.fetchall()
		for s in resp:
			if s:
				sites[idx]={}
				sites[idx]['name']=s[0]
				sites[idx]['types']=s[1]
				sites[idx]['center']=s[2].replace(' ',',')
	con.close()
	return sites
	
def query_routes(routes_ids):
	con = psycopg2.connect("dbname=pistes-mapnik user=mapnik")
	cur = con.cursor()
	routes={}
	for idx in routes_ids:
		cur.execute("select route_name, \"piste:type\", ST_AsLatLonText(st_centroid(ST_Transform(way,4326)), 'D.DDDDD'), color, colour from planet_osm_line where osm_id = %s and \"piste:type\" is not null"\
		%(idx))
		resp=cur.fetchall()
		for s in resp:
			if s:
				routes[idx]={}
				routes[idx]['name']=s[0]
				routes[idx]['types']=s[1]
				routes[idx]['center']=s[2].replace(' ',',')
				if not s[3]: routes[idx]['color']=s[4]
				else:  routes[idx]['color']=s[3]
	con.close()
	return routes
	
def query_ways(ways_ids):
	con = psycopg2.connect("dbname=pistes-mapnik user=mapnik")
	cur = con.cursor()
	ways={}
	for idx in ways_ids:
		cur.execute("select name, \"piste:type\", ST_AsLatLonText(st_centroid(ST_Transform(way,4326)), 'D.DDDDD'), \"piste:difficulty\", \"piste:grooming\", \"piste:lit\" from planet_osm_line where osm_id = %s and \"piste:type\" is not null;"\
		%(idx))
		resp=cur.fetchall()
		for s in resp:
			if s:
				ways[idx]={}
				ways[idx]['name']=s[0]
				ways[idx]['types']=s[1]
				ways[idx]['center']=s[2].replace(' ',',')
				ways[idx]['difficulty']=s[3]
				ways[idx]['grooming']=s[3]
				ways[idx]['lit']=s[3]
	con.close()
	return ways

def query_aerialways(ways_ids):
	con = psycopg2.connect("dbname=pistes-mapnik user=mapnik")
	cur = con.cursor()
	aerialways={}
	for idx in ways_ids:
		cur.execute("select name, aerialway, ST_AsLatLonText(st_centroid(ST_Transform(way,4326)), 'D.DDDDD') from planet_osm_line where osm_id = %s and aerialway is not null;"\
		%(idx))
		resp=cur.fetchall()
		for s in resp:
			if s:
				aerialways[idx]={}
				aerialways[idx]['name']=s[0]
				aerialways[idx]['types']=s[1]
				aerialways[idx]['center']=s[2].replace(' ',',')
	con.close()
	return aerialways
#6.46,46.83
#~ n=sys.argv[1]
#~ r=sys.argv[2]
#~ sites, entrances, routes, ways = query_ids('',n,r)
#~ print query_sites(sites)
#~ print query_routes(routes)
#~ print query_ways(ways)
#~ print query_aerialways(ways)

