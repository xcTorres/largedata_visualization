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
	/*添加底图*/
	map =L.map(mapid,{
		maxZoom: 18,
		minZoom: 0
    }).setView([40.7518,-73.9819],10);
	
	// "http://{s}.tile.osm.org/{z}/{x}/{y}.png"
	// FeatureGroup is to store editable layers 
	var maptile = L.tileLayer(
	//"http://{s}.tile.osm.org/{z}/{x}/{y}.png"
	"http://{s}.tiles.mapbox.com/v4/cicerolp.mgdebfa9/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiY2ljZXJvbHAiLCJhIjoia1IxYmtfMCJ9.3EMmwKCCFN-hmsrQY4_wUQ"
	,{
		opacity:0.7,
		nowrap:true
	});
	maptile.addTo(map);
	
	
	// // 添加地图工具栏
	// map.drawnItems = new L.FeatureGroup();
    // map.drawnItems.addTo(map);

    // map.editControl = new L.drawLocal.draw({
		// draw: {
			// rectangle: true,
			// //polygon: false,
			// polyline: false,
			// circle: false,
			// marker: false,
			// polygon: { allowIntersection: false }
		// },
		// edit: {
			// featureGroup: map.drawnItems
		// }
    // });
    // map.editControl.setDrawingOptions({
		// rectangle:{ shapeOptions:{color: this.nextColor(), weight: 2,
					 // opacity:.9}},
		// polygon:{ shapeOptions:{color: this.nextColor(), weight: 2,
					 // opacity:.9}}
    // });

    // map.editControl.addTo(map);
	
    // map.on('draw:created', function (e) {
		// drawCreated(e);
    // });

	// map.on('draw:drawstop',function(e) {
		// drawstop(e);
	// });
	
	heatmap  = new L.Heatmap().addTo(map);
	
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
