
var callbacks = null;

var bounds = null, where = "";
var time_from = "2015-01-01" ;
var time_to = "2015-12-30";
var curr_region = null, curr_where = null;

var update = false;
var update_tile = false;

var total_count = 0, curr_count = 0;

var map;
var heatmap = null;

var url = "http://192.168.0.17:10086";
var dataset = "taxi";
var BRIGHTNESS = -13;
var PLOTTING_MODE = "rect";
var PLOTTING_COLOR_SCALE = "ryw";
var PLOTTING_TRANSFORM = "density_scaling";

var time_series = [];
$.ajaxSetup({
    timeout: 20000 //Time in milliseconds
});


function removeByValue(arr, val) {
  for(var i=0; i<arr.length; i++) {
    if(arr[i] == val) {
      arr.splice(i, 1);
      break;
    }
  }
}



var cacheLength = 300;
// 缓存热图数据
function createCache() {
    // 作用：用来记录存储到缓存中key的顺序
    var cache = {},
    // 作用：对缓存进行增删改查
        keyArr = [];

    return function(key, value) {
        if(value === undefined) {
            return cache[key];
        }

        if(cache[key] === undefined) {
            // push 方法的返回值：添加数据之后的长度
            if(keyArr.push(key) > cacheLength) {
                delete cache[ keyArr.shift() ];
            }
        }
        cache[key] = value;
    };
}

var heatmapCache = createCache();