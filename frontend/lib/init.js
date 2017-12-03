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
		maxZoom: 17,
		minZoom: 2,
		maxBounds: [
			//south west
			[-85, -180],
			//north east
			[85, 180]
			],
		noWrap: true,
		layers: mapbox
    }).setView([40.7518,-73.9819],7);
	
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
	
	map.on('moveend zoomend', function() {
		
		getTimeseries();
	});
	
	
	getTimeseries();
			

	heatmap  = new L.Heatmap().addTo(map);
	heatmap.setZIndex(4);
	
	$('input[type=radio][name=dataset]').click(function() {
        if (this.value == 'nyc_taxi') {
			
			dataset = "taxi";
			time_from = "2015-01-01 00:00:00";	
			time_to = "2016-06-30 00:00:00";
			PLOTTING_TRANSFORM = "density_scaling";
			getTimeseries();
			map.setView([40.7518,-73.9819],7);

			

        }
        else if (this.value == 'crime') {
			dataset = "crime";
			time_from = "2015-01-01 00:00:00";	
			time_to = "2017-06-30 00:00:00";
			PLOTTING_TRANSFORM = "density_scaling";
			getTimeseries();
			map.setView([41.7863,-87.8105],7);
			
        }
		else if (this.value == 'brightkite') {
			
			dataset = "brightkite";
           	time_from = "2008-01-01 00:00:00";	
			time_to = "2011-01-31 00:00:00";
			PLOTTING_TRANSFORM = "no_scaling";
			getTimeseries();
			map.setView([20,0],2);
			

        }
    });
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

function getTimeseries(){
	
	var sw = map.getBounds().getSouthWest();
	var ne = map.getBounds().getNorthEast(); 
	var bounds = sw.lng.toFixed(4)+","+ sw.lat.toFixed(4)+","+ne.lng.toFixed(4)+","+ne.lat.toFixed(4);

	
	$.get(url+'/time_series', {
			
			dataset:dataset,
			level : map.getZoom(),
			bounds: bounds,
			time_from: time_from,
			time_to: time_to
			
		},  function(data,textStatus){
			
			
			
			
			time_series = [];
			for (i in data  ) {
				d = moment(i).format("YYYY-MM-DD HH:mm:ss");
				if(dataset=="crime"){
					if(data[i]<2000)
						time_series.push([d,data[i]]);
				}else{
					time_series.push([d,data[i]]);
				}
			}
				
			time_series.sort(function(x, y){
			   
			   return d3.ascending(x[0],y[0]);
			});
			
				
			d3.select("svg").remove();
			loadLineChart(time_series,"date");
			
		},"json");	
}
