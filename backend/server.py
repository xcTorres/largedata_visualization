from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse,parse_qs
import datetime
import jpype
import matplotlib.pyplot as plt
import happybase
import time
import mercantile

from SocketServer import ThreadingMixIn

HOST_IP = ''
PORT = 10086
dataset = ""
# q_time1 = []
# q_time2 = []
def transToStamp(t):

    timeArray = datetime.datetime.strptime(t, "%Y-%m-%d")

    return timeArray.date()

def quadkey_to_num(qk):
    number = 0
    for i, digit in enumerate(qk):
        number  |= int(digit)
        if i != len(qk)-1:
            number = number << 2

    return str(len(qk)) + ":" + str(number)


def  check_bounds(bounds):

    new_bounds = []

    new_bounds.append(max(-180,float(bounds[0])))
    new_bounds.append(max(-85,float(bounds[1])))
    new_bounds.append(min(180,float(bounds[2])))
    new_bounds.append(min(85,float(bounds[3])))

    return new_bounds


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """


class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)

        if url.path == '/tile':


            query_components = parse_qs(urlparse(self.path).query)
            dataset = query_components["dataset"][0]
            level = query_components["level"][0]
            x = query_components["x"][0]
            y = query_components["y"][0]

            time_from = transToStamp( query_components["time_from"][0] )
            time_to = transToStamp( query_components["time_to"][0] )

            # start = time.time()

            tile_quadkey = mercantile.quadkey( int(x),int(y),int(level) )
            tile_id = quadkey_to_num(tile_quadkey)
            print tile_id , str(time_from) ,str(time_to)
            jpype.attachThreadToJVM()
            hbase_response =cp.spatialSum("nycTaxi", tile_id, str(time_from), str(time_to))

            print hbase_response
            # end = time.time()
            # print "query_time" + ": " + str(end - start)
            #
            #
            # q_time1.append(end - start)


            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()


            self.wfile.write(hbase_response)




            # if len(q_time1) == 20:
            #     print "hundred"
            #     plt.plot(range(len(q_time1)), q_time1)
            #     plt.ylabel('tile query time')
            #     plt.axis([1, 20, 0, 2])
            #     print float(sum(q_time1)) / len(q_time1)
            #     plt.show()

            return

        if url.path == '/time_series':
            query_components = parse_qs(urlparse(self.path).query)

            dataset = query_components["dataset"][0]
            level = query_components["level"][0]
            bounds = query_components["bounds"][0]
            bounds = bounds.split(",")
            time_from = transToStamp( query_components["time_from"][0] )
            time_to = transToStamp( query_components["time_to"][0])

            start = time.time()

            new_bounds =  check_bounds(bounds)
            tiles = mercantile.tiles(new_bounds[0],new_bounds[1],new_bounds[2], \
                                     new_bounds[3], [int(level), ])

            tile_numbers = []
            for tile in list(tiles):
                t_quadkey = mercantile.quadkey(tile)
                t_num = quadkey_to_num(t_quadkey)
                tile_numbers.append(t_num)

            tile_numbers = ' '.join(str(x) for x in tile_numbers)
            jpype.attachThreadToJVM()
            res  = cp.timeSeriesCount(dataset,tile_numbers,str(time_from),str(time_to))

            end = time.time()
            print "query_time" + ": " + str(end - start)


            # q_time2.append(end - start)


            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(res)

            # if len(q_time2) == 20:
            #     print "hundred"
            #     plt.plot(range(len(q_time2)), q_time2)
            #     plt.ylabel('timeseries query time')
            #     plt.axis([1, 20, 0, 1])
            #     print float(sum(q_time2)) / len(q_time2)
            #     plt.show()

            return


if __name__ == '__main__':
    jpype.startJVM(jpype.getDefaultJVMPath(), "-ea ", "-Djava.class.path=%s" % ('/tmp/GroupByInterface.jar'))
    jpype.attachThreadToJVM()
    coprocessor = jpype.JClass("com.hbase.client.MainEntrance")
    cp = coprocessor()

    httpd = ThreadedHTTPServer((HOST_IP, PORT), myHandler)
    print "serving at port", PORT
    httpd.serve_forever()




