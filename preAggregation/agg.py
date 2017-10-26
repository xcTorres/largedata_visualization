import os
import sys
import  math
import datetime as dt
from collections import Counter
from collections import OrderedDict

from pyspark import SparkContext
from pyspark import SparkConf

import mercantile

## transfor time to stamp
# base_time = "2016-01-01 00:00:00"
# def transToStamp(t):
#
#     timeArray = dt.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
#     base_timeArray = dt.datetime.strptime(base_time, "%Y-%m-%d %H:%M:%S")
#     stamp = ( timeArray - base_timeArray).total_seconds() / 3600
#
#     return int(stamp)+1

def transToStamp(t):

    timeArray = dt.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

    d = timeArray.date()
    #h = timeArray.time().hour

    #return str(d)+"_"+str(h)
    return str(d)



def lnglat_to_quad( lon_deg, lat_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    quadkey = mercantile.quadkey(xtile, ytile, zoom)

    return quadkey

def quadkey_to_num(qk):
    number = 0
    for i, digit in enumerate(qk):
        number  |= int(digit)
        if i != len(qk)-1:
            number = number << 2
    return number

def process( line, low_level,up_level ):
    try:
        lng = float(line[5])
        lat = float(line[6])
    except:
        return

    stamp = transToStamp(line[1])

    result = []
    for i in range(low_level,up_level+1):
        tile_id = lnglat_to_quad(lng,lat,i)
        quadkey_to_num(tile_id)
        result.append( (tile_id,stamp) )
    return result

def process2( line ):
    quad_key =  line[0]

    time_series =  dict(line[1])

    quadkey_pixel = mercantile.quadkey_to_tile(quad_key)

    result = []
    if quadkey_pixel.z >= 12:

        t = mercantile.tile(*mercantile.ul(quadkey_pixel.x, quadkey_pixel.y, quadkey_pixel.z) + (quadkey_pixel.z - 8,))
        t_quadkey = mercantile.quadkey(t)
        t_num = quadkey_to_num(t_quadkey)

        origin_x  = t.x * math.pow(2,8)
        origin_y  = t.y * math.pow(2,8)
        pixel_x = int(quadkey_pixel.x  -  origin_x)
        pixel_y = int(quadkey_pixel.y  - origin_y)

        for k,v in time_series.iteritems():
            tile_id = str(t_num) + ":" + str(k)

            index = int(pixel_y*math.pow(2,8)+pixel_x)
            kv = (index,v)
            result.append( (tile_id,kv) )

    return result


def sort_timeseries(a):

    l = list(a)
    counts = dict(Counter(l))
    # sorted_time = OrderedDict(sorted(counts.items())).items()

    # sorted_agg = []
    # for_aggregate = 0
    # for i in range(0, len(sorted_time)):
    #     cur_timetag = sorted_time[i][0]
    #     kv = {}

        # if i == 0:
        #     for_aggregate = sorted_time[i][1]
        # else:
        #     for_aggregate = sorted_time[i][1] + for_aggregate

        # kv[cur_timetag] = for_aggregate
        # sorted_agg.append(kv)

    # return sorted_agg
    return counts

def fillzero(a):

    data = list(a)

    result = [0] * 256 *256

    for ele in data:

        index = ele[0]
        result[index] = ele[1]

    return result


if __name__ == '__main__':

    sc = SparkContext()
    csvfile = sc.textFile("hdfs://192.168.0.17:8020/user/root/ny_taxi/yellow_tripdata_2016-0[1-6].csv")
    all = csvfile.map(lambda line: line.split(","))

    header = all.first()
    content = all.filter(lambda line: line[0] != header[0] ).map( lambda line: process(line,12,22) ).flatMap(lambda x: x) \
        .groupByKey().mapValues(sort_timeseries)
    content = content.map(lambda line: process2(line)).flatMap(lambda x:x).groupByKey().mapValues(list)
    content.saveAsTextFile("/user/root/taxi_temp/")
