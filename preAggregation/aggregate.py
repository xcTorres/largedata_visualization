import  sys
import mercantile
import csv
import math
import datetime as dt
import time
#from collections import defaultdict
## transfor time to stamp
base_time = "2016-01-01 00:00:00"
def transToStamp(t):

    timeArray = dt.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    base_timeArray = dt.datetime.strptime(base_time, "%Y-%m-%d %H:%M:%S")
    stamp = ( timeArray - base_timeArray).total_seconds() / 3600

    return int(stamp)+1

###save2File
def save2File(d,file):
    for item in d:
        if item:
            file.write(''.join(item))

def Lnglat2Tile( lon_deg, lat_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)

if __name__ == '__main__':

    start = time.time()
    data = {}
    with open(sys.argv[1],"rb") as csvfile:
        reader = csv.DictReader(csvfile)
        i=0
        level = int(sys.argv[2])
        print level
        for row in reader:
            t = row['tpep_pickup_datetime']
            lng  = float(row['pickup_longitude'])
            lat  = float(row['pickup_latitude'])

            if lng==0.0 or lat==0.0:
                continue

            x,y  = Lnglat2Tile(lng ,lat,level)
            #lnglat = mercantile.ul(x + 0.5, y + 0.5, 19)
            #spatial_key = mercantile.quadkey(x, y, 19)
            #print lng,lat
            #print lnglat
            tile_id =  str(level) + '_' +str(x) + '_' + str(y)
            #print tile_id
            stamp = transToStamp(t)

            if tile_id in data:
                if stamp in data[tile_id]:
                    data[tile_id][stamp] += 1
                else:
                    data[tile_id][stamp] = 1
            else:
                data[tile_id] = {}
                data[tile_id][stamp] = 1
            #i += 1
            #if (i%100000) == 0:
                #print i
        csvfile.close()

    end = time.time()
    print "agg_time" + ": " + str(end - start)

    start = time.time()
    with open('/home/xc/nyc_taxi/yellow/aggregate/'+str(level)+'.csv', 'w') as csvfile:
        fieldnames = ['tile_id', 'time_value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for k in data:
            writer.writerow({'tile_id': k, 'time_value': data[k]})

        csvfile.close()

    end = time.time()
    print "save_time" + ": " + str(end - start)

