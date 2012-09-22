/*
pistes-nordiques.js
Javascript code for www.pistes-nordiques.org website
Copyright (C) 2011  Yves Cainaud

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/
// MODE
var mode="raster";
var m="raster";
var zoomBar;
function switch2vector() {
    if (mode == "raster") {
        loadjscssfile("js/pistes-nordiques-plus.js", "js");
        map.getLayersByName("Pistes Tiles LZ")[0].setVisibility(false);
        map.getLayersByName("Pistes Tiles")[0].setVisibility(false);
        document.getElementById('vector-help').style.display='none';
        // extended menu controls
        document.getElementsByName("Mode")[0].checked=true;
        document.getElementsByName("live")[0].disabled=false;
        document.getElementsByName("live")[1].disabled=false;
        document.getElementsByName("live")[2].disabled=false;
        $("status").innerHTML = '<b style="color:#FFFFFF;">'+_('loading...')+'</b>'; 
        $("status").style.backgroundColor = '#FF7800';
        
        mode="vector";
        map.getControlsByClass("OpenLayers.Control.Permalink")[0].updateLink();
    }
}
function switch2raster() {
    if (mode == "vector") {
        // first destroy the selet and highlight controls
        var ctrls= map.getControlsByClass("OpenLayers.Control.SelectFeature");
        for (var c in ctrls) {ctrls[c].destroy();}
        // then layers
        var lays = map.getLayersByClass("OpenLayers.Layer.Vector");
        for (var l in lays) {lays[l].destroy();}
        var marks = map.getLayersByClass("OpenLayers.Layer.Markers");
        for (var m in marks) {marks[m].destroy();}

        removejscssfile("js/pistes-nordiques-plus.js", "js");
        map.getLayersByName("Pistes Tiles LZ")[0].setVisibility(true);
        map.getLayersByName("Pistes Tiles")[0].setVisibility(true);
        document.getElementById('vector-help').style.display='inline';
        document.getElementById('routing').style.display='none';
        // extended menu controls
        document.getElementsByName("Mode")[1].checked=true;
        document.getElementsByName("live")[0].disabled=true;
        document.getElementsByName("live")[1].disabled=true;
        document.getElementsByName("live")[2].disabled=true;
        
        mode="raster";
        map.getControlsByClass("OpenLayers.Control.Permalink")[0].updateLink();
    }
}
function setmode(m){
    if (m == "vector") {switch2vector();}
    if (m == "raster") {switch2raster();}
}
function loadjscssfile(filename, filetype){
 if (filetype=="js"){ //if filename is a external JavaScript file
  var fileref=document.createElement('script')
  fileref.setAttribute("type","text/javascript")
  fileref.setAttribute("src", filename)
 }
 else if (filetype=="css"){ //if filename is an external CSS file
  var fileref=document.createElement("link")
  fileref.setAttribute("rel", "stylesheet")
  fileref.setAttribute("type", "text/css")
  fileref.setAttribute("href", filename)
 }
 if (typeof fileref!="undefined")
  document.getElementsByTagName("head")[0].appendChild(fileref)
}
function removejscssfile(filename, filetype){
 var targetelement=(filetype=="js")? "script" : (filetype=="css")? "link" : "none" //determine element type to create nodelist from
 var targetattr=(filetype=="js")? "src" : (filetype=="css")? "href" : "none" //determine corresponding attribute to test for
 var allsuspects=document.getElementsByTagName(targetelement)
 for (var i=allsuspects.length; i>=0; i--){ //search backwards within nodelist for matching elements to remove
  if (allsuspects[i] && allsuspects[i].getAttribute(targetattr)!=null && allsuspects[i].getAttribute(targetattr).indexOf(filename)!=-1)
   allsuspects[i].parentNode.removeChild(allsuspects[i]) //remove element by calling parentNode.removeChild()
 }
}
function get_page(url){
    var oRequest = new XMLHttpRequest();
    oRequest.open("GET",url,false);
    oRequest.setRequestHeader("User-Agent",navigator.userAgent);
    oRequest.send()
    response = oRequest.responseText;
    response = response.replace("../","")
    return response;
}
function toggleMenu() {
    var em = document.getElementById('extendedmenu');
    var sl = document.getElementById('slide');
    // At loadtime, m.style.display=""
    if (em.style.display == "none" || em.style.display == "") {
        em.style.display ='inline';
        sl.innerHTML='<a onclick="toggleMenu();" ></br>&#176;</br>&#176;</br>&#176;</a>';
        EXT_MENU=true;
        }
    else if (em.style.display == "inline") {
        em.style.display = 'none';
        sl.innerHTML='<a onclick="toggleMenu();" ></br>&#8226;</br>&#8226;</br>&#8226;</a>';
        EXT_MENU=false;
        }
    map.getControlsByClass("OpenLayers.Control.Permalink")[0].updateLink();
    resize_sideBar();
    return true;
    
}
function showMenu() {
    var em = document.getElementById('extendedmenu');
    var sl = document.getElementById('slide');
    em.style.display ='inline';
    sl.innerHTML='<a onclick="toggleMenu();" ></br>&#176;</br>&#176;</br>&#176;</a>';
    EXT_MENU=true;
    resize_sideBar();
    return true;
    
}
function close_sideBar() {
    document.getElementById('sideBar').style.display='none';
}
function show_about() {
    document.getElementById('sideBar').style.display='inline';
    url = 'iframes/about.'+iframelocale+'.html';
    content = get_page(url).replace('**update**',get_update()).replace('**length**',get_length()).replace('**modis-update**',get_modisupdate());
    document.getElementById('sideBarContent').innerHTML = content;
    document.getElementById('sideBarContent').style.display='inline';
    document.getElementById('sideBarTitle').innerHTML='&nbsp;'+_('about');
}
function show_help() {
    document.getElementById('sideBar').style.display='inline';
    url = 'iframes/quickhelp.'+iframelocale+'.html';
    content = get_page(url);
    document.getElementById('sideBarContent').innerHTML = content;
    document.getElementById('sideBarContent').style.display='inline';
    document.getElementById('sideBarTitle').innerHTML='&nbsp;'+_('help');
}
function show_edit() {

    document.getElementById('sideBar').style.display='inline';
    document.getElementById('sideBarContent').style.display='inline';
    document.getElementById('sideBarTitle').innerHTML='&nbsp;'+_('edit').replace('<br/>',' ');
    if (map.getZoom() > 12) {
        html = '<p>&nbsp;'+_('edit_the_map_using')+'</p>'
         +'<p>&nbsp;'+_('edit_the_map_explain')+'</p>'
         +'<hr class="hrmenu">'
         +'<p><a href="iframes/how-to-'+locale+'.html" target="blank">'+_('how_to')+'</a></p>'
         +'<hr class="hrmenu">'
         +'<p style="text-align:center;">'
         +'<a id="permalink.potlatch" href="" target="blank"><img src="pics/potlatch.png" ></a>'
         +'<hr class="hrmenu">'
         +'</p><p style="text-align:center;">'
         +'<a id="permalink.potlatch2" href="" target="blank"><img src="pics/potlatch2.png" ></a>'
         +'</p>'
         +'<hr class="hrmenu">';
        document.getElementById('sideBarContent').innerHTML=html;
        var permalink_potlatch = new OpenLayers.Control.Permalink("permalink.potlatch",
        "http://www.openstreetmap.org/edit",{'createParams': permalink1Args});
        map.addControl(permalink_potlatch);
        var permalink_potlatch2 = new OpenLayers.Control.Permalink("permalink.potlatch2",
        "http://www.openstreetmap.org/edit",{'createParams': permalink2Args});
        map.addControl(permalink_potlatch2);
    }
    else {
        document.getElementById('sideBarContent').innerHTML='&nbsp;'+_('zoom_in');
        
    }
}
function show_profile() {
    document.getElementById('sideBar').style.display='inline';
    document.getElementById('sideBarTitle').innerHTML='&nbsp;'+_('TOPO');
    if (mode=="raster") {
        document.getElementById('sideBarContent').innerHTML=_('interactive_map_only');
    }else if (map.getZoom() <= 13) {
        document.getElementById('sideBarContent').innerHTML=_('zoom_in');
    }
}
function show_legend() {
    document.getElementById('sideBar').style.display='inline';
    document.getElementById('sideBarContent').style.display='inline';
    document.getElementById('sideBarTitle').innerHTML='&nbsp;'+_('map_key').replace('<br/>',' ');
    html = '<p>'+_('key-color')
    + '<a target="blank" href="http://wiki.openstreetmap.org/wiki/Proposed_features/Tag:route%3Dpiste"> (1)</a>.</p>'
    + '<p><img src="pics/key-normal.png" style="float:left" >'
    + '<b>'+_('key-normal')+'</b>'+'&nbsp;&nbsp;'+_('key-normal_exp')+'</p>'
    + '<p class="clear"><img src="pics/key-intermediate.png" style="float:left" >'
    + '<b>'+_('key-intermediate')+'</b>'+'&nbsp;&nbsp;'+_('key-intermediate_exp')+'</p>'
    + '<p class="clear"><img src="pics/key-hard.png" style="float:left" >'
    + '<b>'+_('key-hard')+'</b>'+'&nbsp;&nbsp;'+_('key-hard_exp')+'</p>'
    + '<p class="clear"><img src="pics/key-unknow.png" style="float:left" >'
    + '<b>'+_('key-unknow')+'</b>'+'&nbsp;&nbsp;'+_('key-unknow_exp')
    +'<a onclick="show_edit();"> ('+ _('edit')+')</a></p>'
    +'<p>'+_('learn-difficulties')
    +'<a target="blank" href="http://wiki.openstreetmap.org/wiki/Proposed_features/Piste_Maps#Difficulty"> (2)</a>.</p>'         +'<hr class="hrmenu">'
         +'<p><a href="iframes/how-to-en.html" target="blank">'+_('how_to')+'</a></p>'
         +'<hr class="hrmenu">';
    document.getElementById('sideBarContent').innerHTML=html;
}
//======================================================================
// INIT

document.onkeydown = checkKey;

// register 'enter' and 'esc' keyboard hit
function checkKey(e) {
    var keynum;
    if (window.event) keynum = window.event.keyCode; //IE
    else if (e) {
        keynum = e.which;
        if (keynum == undefined)
        {
        e.preventDefault();
        keynum = e.keyCode
        }
    }
    
    if(keynum == 27) {
        close_sideBar();
        // close extendedmenu
        var em = document.getElementById('extendedmenu');
        var sl = document.getElementById('slide');
        if (em.style.display == "inline") {
        em.style.display = 'none';
        sl.innerHTML='<a onclick="toggleMenu();" ></br>&#8226;</br>&#8226;</br>&#8226;</a>';
        }
        clearRoute();
        //clear routing
        //clearRoute();
        //$('routing').style.display='none';
        }
    if(keynum == 13) {
        // fires nominatim search
        nominatimSearch(document.search.nom_search.value);
        }
}

function get_length(){
    var oRequest = new XMLHttpRequest();
    oRequest.open("GET",'data/ways_length.txt',false);
    oRequest.setRequestHeader("User-Agent",navigator.userAgent);
    oRequest.send()
    return oRequest.responseText;
}

function get_update(){
    var oRequest = new XMLHttpRequest();
    oRequest.open("GET",'data/update.txt',false);
    oRequest.setRequestHeader("User-Agent",navigator.userAgent);
    oRequest.send();
    var date=oRequest.responseText.split('T')[0];
    var H=oRequest.responseText.split('T')[1].split('\\')[0];
    var M=oRequest.responseText.split('T')[1].split('\\')[1];
    var DHM=date +' '+ H+M+'UTC';
    return DHM;
}

function get_modisupdate(){
    var oRequest = new XMLHttpRequest();
    oRequest.open("GET",'data/modis-update.txt',false);
    oRequest.setRequestHeader("User-Agent",navigator.userAgent);
    oRequest.send();
    var period=oRequest.responseText.split(' ')[5];
    return period;
}
function stopRKey(evt) {
    // disable the enter key action in a form.
  var evt = (evt) ? evt : ((event) ? event : null);
  var node = (evt.target) ? evt.target : ((evt.srcElement) ? evt.srcElement : null);
  if ((evt.keyCode == 13) && (node.type=="text"))  {return false;}
}

function getWinHeight(){
      var myWidth = 0, myHeight = 0;
      if( typeof( window.innerWidth ) == 'number' ) {
        //Non-IE
        myWidth = window.innerWidth;
        myHeight = window.innerHeight;
      } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
        //IE 6+ in 'standards compliant mode'
        myWidth = document.documentElement.clientWidth;
        myHeight = document.documentElement.clientHeight;
      } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
        //IE 4 compatible
        myWidth = document.body.clientWidth;
        myHeight = document.body.clientHeight;
      }
    return parseInt(myHeight);
}

function resize_sideBar() {
    document.getElementById('sideBar').style.height= (getWinHeight() - 50
        - document.getElementById('menu').offsetHeight
        - document.getElementById('extendedmenu').offsetHeight)+"px";
    document.getElementById('sideBarContent').style.height= (getWinHeight() - 73
        - document.getElementById('menu').offsetHeight
        - document.getElementById('extendedmenu').offsetHeight)+"px";
        
    //document.getElementById('search_result').style.height= getWinHeight()-25-110-40;
    //document.getElementById('snow_info').style.height= getWinHeight()-25-110-40;
    //document.getElementById('add_link').style.height= getWinHeight()-25-110-40;
    //document.getElementById('topo').style.height= getWinHeight()-25-110-40;
    //document.getElementById('edit').style.height= getWinHeight()-25-110-40;
    //document.getElementById('about').style.height= getWinHeight()-25-110-40;
    //document.getElementById('help').style.height= getWinHeight()-25-110-40;
}

function page_init(){
        document.onkeypress = stopRKey; 
        updateZoom();
        initFlags();
        resize_sideBar();
        window.onresize = function(){resize_sideBar();}
}

function loadend(){
    if (EXT_MENU) {showMenu();}
    
}
//======================================================================
// NOMINATIM
    function setCenterMap(nlon, nlat, zoom) {
        nlonLat = new OpenLayers.LonLat(nlon, nlat).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
        map.setCenter(nlonLat, zoom);
        document.getElementById('sideBar').style.display='none';
    }

    function nominatimSearch(string) {
        if (string == '') {return false;};
        close_sideBar();
        document.search.nom_search.value='';
        document.getElementById('sideBar').style.display='inline';
        //document.getElementById('search_result').style.display='inline';
        document.getElementById('sideBarTitle').innerHTML='&nbsp;'+_('search_results');
        string=string.replace(" ","+");
        var oRequest = new XMLHttpRequest();
        //oRequest.open("GET",'http://open.mapquestapi.com/nominatim/v1/search?format=xml&q='+string,false);
        oRequest.open("GET",'cgi/nominatim.cgi/search?format=xml&place='+string,false);
        oRequest.setRequestHeader("User-Agent",navigator.userAgent);
        oRequest.send();
        setTimeout('',500);
        var responseXML = oRequest.responseXML;
        var response = responseXML.getElementsByTagName('place');
        
        var htmlResponse='<p><ul>';
        
        for (var i=0;i<response.length;i++) {
            htmlResponse += '<li><a onclick="setCenterMap('
            + response[i].getAttribute('lon') +','
            + response[i].getAttribute('lat') +','
            + 14 +');">'
            + response[i].getAttribute('display_name') +'</a></li><br/>';
        }
        htmlResponse += '</p></ul> <p>Nominatim Search Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png"></p>';
        
        document.getElementById("sideBarContent").innerHTML = htmlResponse;
    }

//======================================================================
// MAP

var lat=46.82084;
var lon=6.39942;
var zoom=2;//2
var EXT_MENU=false;
var map;

var highlightCtrl, selectCtrl;

// a dummy proxy script is located in the directory to allow use of wfs
OpenLayers.ProxyHost = "cgi/proxy.cgi?url=";

// Redirect permalink
if (location.search != "") {
    //?zoom=13&lat=46.82272&lon=6.87183&layers=B0TT
    var x = location.search.substr(1).split("&")
    for (var i=0; i<x.length; i++)
    {
        if (x[i].split("=")[0] == 'zoom') {zoom=x[i].split("=")[1];}
        if (x[i].split("=")[0] == 'lon') {lon=x[i].split("=")[1];}
        if (x[i].split("=")[0] == 'lat') {lat=x[i].split("=")[1];}
        if (x[i].split("=")[0] == 'e') {EXT_MENU=x[i].split("=")[1];}
        if (x[i].split("=")[0] == 'm') {m=x[i].split("=")[1];} // not used
    }
    //Then hopefully map_init() will do the job when the map is loaded
}

function zoomSlider(options) {

    this.control = new OpenLayers.Control.PanZoomBar(options);

    OpenLayers.Util.extend(this.control,{
        draw: function(px) {
            // initialize our internal div
            OpenLayers.Control.prototype.draw.apply(this, arguments);
            px = this.position.clone();

            // place the controls
            this.buttons = [];

            var sz = new OpenLayers.Size(24,24);
            var centered = new OpenLayers.Pixel(px.x+sz.w/2, px.y);
            this._addButton("zoomin", "zoom-plus-mini.png", centered.add(0, 5), sz);
            centered = this._addZoomBar(centered.add(0, sz.h + 5));
            this._addButton("zoomout", "zoom-minus-mini.png", centered, sz);
            return this.div;
        }
    });
    return this.control;
}

function updateZoom() {
    $('zoom').innerHTML= map.getZoom();
}

function get_osm_url(bounds) {
    var res = this.map.getResolution();
    var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
    var y = Math.round((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
    var z = this.map.getZoom();
    var limit = Math.pow(2, z);

    if (y < 0 || y >= limit) {
        return OpenLayers.Util.getImagesLocation() + "404.png";
    } else {
        x = ((x % limit) + limit) % limit;
        return this.url + z + "/" + x + "/" + y + ".png";
    }
}

function get_tms_url(bounds) {
        var res = this.map.getResolution();
        var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var y = Math.round((bounds.bottom - this.tileOrigin.lat) / (res * this.tileSize.h));
        var z = this.map.getZoom();
        var limit = Math.pow(2, z);
        //if (mapBounds.intersectsBounds( bounds ) && z >= mapMinZoom && z <= mapMaxZoom ) {
      if (y < 0 || y >= limit)
        {
          return null;
        }
      else
        {
          return this.url + z + "/" + x + "/" + y + ".png"; 
        }
    } 

function toggleBaseLayer(){
    var mq=map.getLayersByName("MapQuest")[0];
    var osm=map.getLayersByName("OSM")[0];
    if (mq) {
        map.removeLayer(mq);
        var mapnik = new OpenLayers.Layer.OSM("OSM");
        map.addLayer(mapnik);

    } else {
        map.removeLayer(osm);
        var arrayMapQuest = ["http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
            "http://otile2.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
            "http://otile3.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
            "http://otile4.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg"];
        var mapquest = new OpenLayers.Layer.OSM("MapQuest",arrayMapQuest,{visibility: true});
        map.addLayer(mapquest);    }
}

function baseLayers() {

// Layer 1.5
    var mapnik = new OpenLayers.Layer.OSM("OSM");
    //map.addLayer(mapnik);
// Layer 0
    var snowCover = new OpenLayers.Layer.TMS( "Snow Cover",
                    "http://tiles2.pistes-nordiques.org/snow-cover/",
                    {   
                    getURL: get_osm_url,
                    isBaseLayer: false, visibility: true, maxScale: 6000000
                    });
    map.addLayer(snowCover);
// Layer 1
    var arrayMapQuest = ["http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
        "http://otile2.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
        "http://otile3.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
        "http://otile4.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg"];
    var mapquest = new OpenLayers.Layer.OSM("MapQuest",arrayMapQuest);
    map.addLayer(mapquest);
// Layer 2
    var layerGTOPO30 = new OpenLayers.Layer.TMS( "GTOPO30", "http://tiles2.pistes-nordiques.org/gtopo30/",{   
                type: 'png', getURL: get_tms_url, alpha: true, opacity: 0.3,
                isBaseLayer: false, visibility: true, maxScale: 3000000, minScale: 8000000
            });
    map.addLayer(layerGTOPO30);

// Layer 3
    var hillshading = new OpenLayers.Layer.TMS( "Hillshade",
                    "http://tiles.pistes-nordiques.org/tiles-hillshading/",
                    {   
                    getURL: get_osm_url,
					minScale: 3000000,
                    isBaseLayer: false, visibility: true
                    });
    map.addLayer(hillshading);
// layer 4
    var layerContours = new OpenLayers.Layer.XYZ("Contour",
    "http://tiles.pistes-nordiques.org/tiles-contours/",{
            getURL: get_osm_url,
            numZoomLevels: 18, isBaseLayer: false,
            transparent: true, buffer: 0,
            minScale: 200000, visibility: true 
        });
    map.addLayer(layerContours);
// Layer 5
    var PistesTilesLowZoom = new OpenLayers.Layer.XYZ("Pistes Tiles LZ",
    "http://tiles.pistes-nordiques.org/tiles-pistes/",{
            getURL: get_osm_url, 
            isBaseLayer: false, numZoomLevels: 19,
            visibility: true, opacity: 0.8,
            maxScale: 250000
        });
    map.addLayer(PistesTilesLowZoom);
// Layer 6
    var PistesTiles = new OpenLayers.Layer.XYZ("Pistes Tiles",
    "http://tiles.pistes-nordiques.org/tiles-pistes/",{
            getURL: get_osm_url, 
            isBaseLayer: false, numZoomLevels: 19,
            visibility: true, opacity: 0.95,
            minScale: 250000
        });
    map.addLayer(PistesTiles);
// Layer 6
    var PistesTiles2 = new OpenLayers.Layer.XYZ("Pistes Tiles2",
    "http://tiles.pistes-nordiques.org/tiles-pistes2/",{
            getURL: get_osm_url, 
            isBaseLayer: false, numZoomLevels: 19,
            visibility: true, opacity: 0.95,
            minScale: 250000
        });
    map.addLayer(PistesTiles2);
}

function permalink2Args() {
    var args = 
        OpenLayers.Control.Permalink.prototype.createParams.apply(
            this, arguments
        );
    args['editor'] = 'potlatch2';
    return args;
}

function permalink1Args() {
    var args = 
        OpenLayers.Control.Permalink.prototype.createParams.apply(
            this, arguments
        );
    args['editor'] = 'potlatch';
    return args;
}
function permalink0Args() {
    var args = 
        OpenLayers.Control.Permalink.prototype.createParams.apply(
            this, arguments
        );
    args['layers']='';
    args['e'] = EXT_MENU;
    args['m'] = mode;
    return args;
}

function map_init(){
    map = new OpenLayers.Map ("map", {
    controls:[
        //new OpenLayers.Control.PanZoomBar(),
        //to avoid shift+right click annoyance:
        new OpenLayers.Control.Navigation({'zoomBoxEnabled' : false }),
        new OpenLayers.Control.TouchNavigation(),
        new OpenLayers.Control.LayerSwitcher(),
        //new OpenLayers.Control.Attribution(),
        new OpenLayers.Control.Permalink('permalink',window.href,{'createParams': permalink0Args}),
        new OpenLayers.Control.MousePosition()],
        maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
        maxResolution: 156543.0399,
        numZoomLevels: 19,
        units: 'm',
        projection: new OpenLayers.Projection("EPSG:900913"),
        displayProjection: new OpenLayers.Projection("EPSG:4326")
    } );
    zoomBar = new zoomSlider({'div':document.getElementById("paneldiv")});
    zoomBar.zoomStopWidth=24;
    map.addControl(zoomBar);
    
    baseLayers();
// Switch base layer
    map.events.on({ "zoomend": function (e) {
        updateZoom();
        if (map.getZoom() > 6) {
            map.layers[1].setVisibility(true);
            map.layers[1].redraw();
        }
        else {
            map.layers[1].setVisibility(false);
        }
    }
    });

    //################################
    var lonLat = new OpenLayers.LonLat(lon, lat).transform(
        new OpenLayers.Projection("EPSG:4326"),
        new OpenLayers.Projection("EPSG:900913"));
    map.setCenter (lonLat, zoom); 
    //map.getControlsByClass("OpenLayers.Control.PanZoomBar")[0].div.style.top=0;
    map.getControlsByClass("OpenLayers.Control.PanZoomBar")[0].div.style.left=0;
    // map.setCenter moved after the strategy.bbox, otherwise it won't load the wfs layer at first load
    setmode(m);
    map.getControlsByClass("OpenLayers.Control.Permalink")[0].updateLink();
}


