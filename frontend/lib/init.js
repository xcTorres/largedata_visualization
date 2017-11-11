var colors = colorbrewer.Oranges[9];
//var url = "http://127.0.0.1:9001/";
// var url = "./city.json";
// var map;
// var heatmapLayer;
// var bounds = [];
// var time_from = "2016-01-01";	
// var time_to = "2016-03-01";
// var heatmap = null;
function init() {
	
	var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib,opacity:0.2,nowrap:true });
		
	var mapboxurl = "http://{s}.tiles.mapbox.com/v4/cicerolp.mgdebfa9/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiY2ljZXJvbHAiLCJhIjoia1IxYmtfMCJ9.3EMmwKCCFN-hmsrQY4_wUQ",
		mapbox = L.tileLayer(mapboxurl, { maxZoom: 18,opacity:0.5,nowrap:true });

	
	
	
	/*添加底图*/
	map =L.map(mapid,{
		maxZoom: 18,
		minZoom: 0,
		layers: mapbox
    }).setView([40.7518,-73.9819],6);
	
	var baseMaps = {
		"<span style='color: gray'>Mapbox</span>": mapbox,
		"Osm": osm
	};
	L.control.layers(baseMaps).addTo(map);
	
	
	
	var drawnItems = new L.FeatureGroup();
	map.addLayer(drawnItems);

    var drawControl = new L.Control.Draw({
        position: 'topleft',
        draw: {
            polyline: false,
            polygon: true,
            circle: false,
            marker: true,
			circlemarker:false,
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });
    map.addControl(drawControl);
	
	

	map.on(L.Draw.Event.CREATED, function (e) {
        var type = e.layerType,
             layer = e.layer;

        if (type === 'marker') {
            layer.bindPopup('A popup!');
        }

        drawnItems.addLayer(layer);
    });

    map.on(L.Draw.Event.EDITED, function (e) {
        var layers = e.layers;
        var countOfEditedLayers = 0;
        layers.eachLayer(function (layer) {
            countOfEditedLayers++;
        });
        console.log("Edited " + countOfEditedLayers + " layers");
    });
	
	
	heatmap  = new L.Heatmap().addTo(map);
	heatmap.setZIndex(4);
	
	
	
	
	
	
	
	
	
	
	/*添加时间轴*/
	var data_offset1  = "2016-01-01 00:00:00";
	var data_offset2  = "2016-02-02 00:00:00";
	var data_offset3  = "2016-03-03 00:00:00";
	var data_offset4  = "2016-06-04 00:00:00";

	var data =  [ [data_offset1,0],[data_offset2,150],[data_offset3,140],[data_offset4,200]];
	loadLineChart(data, "date");
	// var time_series = new Timeseries("date");
	// time_series.brush_callback = function(start,end){
		// time_from = moment(start).format("YYYY-MM-DD HH:mm:ss");
		
		// time_to = moment(end).format("YYYY-MM-DD HH:mm:ss");
		// console.log(time_to);
		// heatmap.redraw();
		// time_series.redraw();
	// };
	
	// time_series.setData( {data:data},"line");
	// time_series.redraw();	
}

function nextColor(){
    var c =colors.shift();
    colors.push(c);
    return c;
};

function drawCreated(e){
    //add the layer
    map.drawnItems.addLayer(e.layer);
	
	    //set next color
    if (e.layerType == 'rectangle'){
		map.editControl.setDrawingOptions({
			rectangle:{shapeOptions:{color: this.nextColor(),weight: 2,
				     opacity:.9}}
		});
    }

    if (e.layerType == 'polygon'){
		map.editControl.setDrawingOptions({
	    polygon:{shapeOptions:{color: this.nextColor(),weight: 2,
				   opacity:.9}}
		});
    }
	
	var sw = e.layer.getBounds().getSouthWest();
	var ne = e.layer.getBounds().getNorthEast(); 
	bounds = [sw.lng.toFixed(4),sw.lat.toFixed(4),ne.lng.toFixed(4),ne.lat.toFixed(4)];	
	console.log(bounds);
};

function drawstop(e){	

	console.log(bounds);
	//getHeatMap(this.bounds,time_from,time_to);
};
