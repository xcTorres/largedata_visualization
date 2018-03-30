import mercantile,math
from dateutil.parser import *
from dateutil.relativedelta import *
from pyspark import HiveContext
from pyspark import SparkContext
from pyspark.sql.functions import *
from pyspark.sql import functions as F

time_base = parse("2016/01/01 00:00:00")
def transToStamp(t):
    d = parse(t)
    r = relativedelta(d,time_base)
    return r


def lnglat_to_Num(lon, lat, zoom):
    try:
        lat_deg = float(lat)
        lon_deg = float(lon)

        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        qk = mercantile.quadkey(xtile, ytile, zoom)

        number = 0
        for i, digit in enumerate(qk):
            number |= int(digit)
            if i != len(qk) - 1:
                number = number << 2

        return number

    except ValueError, e:
        print "error", e
        return None

def Pixel2Tile(lng,lat,zoom,time):

    result = []
    try:
        Pixel  =  lnglat_to_Num(lng, lat, zoom)
        Tile =  int(Pixel/math.pow(2, 16))
        offset = int(Pixel-Tile*math.pow(2,16))
        stamp = transToStamp(time)


        M = stamp.months
        d = stamp.days
        h = d*24 + stamp.hours

        st_tile_d = str(zoom-8) + ":" + str(Tile) + ":" + "d_" + str(d)


        one = [ {offset:1} ,1 ]

        result.append((st_tile_d,one))
    except:
        return None

    return result


def Tile2Parent(st_tile):

    childId, child = st_tile
    parent = [{},0]

    zoom  = childId.split(":")[0]
    quad_num  = childId.split(":")[1]
    stamp  = childId.split(":")[2]

    parentNum = int(quad_num) / 4
    parentId =  str(int(zoom)-1)+ ":" + str(parentNum) + ":" +stamp

    parent_quad_position = int(quad_num) % 4
    x_offset = 0
    y_offset= 0
    if parent_quad_position in [1,3]:
        x_offset = 128
    if parent_quad_position in [2, 3]:
        y_offset = 128
    for old_pixel, count in child[0].items():
        old_x = (old_pixel) % 256
        old_y = (old_pixel) / 256

        new_x = (x_offset + old_x / 2)
        new_y = (y_offset + old_y / 2)

        new_pixel = int(new_y * (math.pow(2, 8)-1) + new_x)

        if new_pixel in parent[0]:
            parent[0][new_pixel] += child[0].pop(old_pixel)
        else:
            parent[0][new_pixel]  = child[0].pop(old_pixel)

    parent[1] = child[1]
    return (parentId,parent)


def group2Tile(pixels_1,pixels_2):

    pixels_1 = list(pixels_1)
    pixels_2 = list(pixels_2)

    A = pixels_1[0]
    B = pixels_2[0]

    for k, v in B.items():
        if k in A.keys():
            A[k] += v
        else:
            A[k] = v

    pixels_1[1] = pixels_1[1] + pixels_2[1]
    return pixels_1


if __name__ == '__main__':
    sc = SparkContext()
    sql = HiveContext(sc)
    df = (sql.read
          .format("com.databricks.spark.csv")
          .option("header", "true")
          .load("/user/root/ny_taxi/yellow_tripdata_201[5-6]-[0-1][0-9].csv")
          .select(["pickup_longitude", "pickup_latitude", "tpep_pickup_datetime"]))

    df = df.select(F.col("tpep_pickup_datetime").alias("time"), F.col("pickup_longitude").alias("lon"), \
                   F.col("pickup_latitude").alias("lat")).dropna(subset=["lat", "lon", "time"])
    df.printSchema()

    tiles = []
    tile = df.map(lambda record: Pixel2Tile(record.lon, record.lat, 17+8, record.time)) \
            .flatMap(lambda x: '' if x is None else x).reduceByKey(group2Tile)

    tile.persist()
    path = "/user/root/taxi_level/" + str(17)
    tile.saveAsTextFile(path)

    i = 17 - 1
    while (i > 0):
        tile = tile.map(lambda tile_tuple: Tile2Parent(tile_tuple)).reduceByKey(group2Tile)
        tile.persist()
        path = "/user/root/taxi_level/" + str(i)
        tile.saveAsTextFile(path)
        i = i-1