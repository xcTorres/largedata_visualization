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
PORT = 9010
dataset = "nyc_taxi"

def transToStamp(t):

    timeArray = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

    return timeArray.date()

def quadkey_to_num(qk):
    number = 0
    for i, digit in enumerate(qk):
        number  |= int(digit)
        if i != len(qk)-1:
            number = number << 2
    return number
    # return str(len(qk)) + "_" + str(number)
# class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
#     """Handle requests in a separate thread."""
#     pass

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
            level = query_components["level"][0]
            x = query_components["x"][0]
            y = query_components["y"][0]

            time_from = transToStamp( query_components["time_from"][0] )
            time_to = transToStamp( query_components["time_to"][0] )

            start = time.time()

            tile_quadkey = mercantile.quadkey( int(x),int(y),int(level) )
            tile_id = quadkey_to_num(tile_quadkey)

            tile_id_from = str(tile_id) + ":" + str(time_from)
            tile_id_to = str(tile_id) + ":" + str(time_to)

            jpype.attachThreadToJVM()
            hbase_response =cp.mutiSum(dataset, tile_id_from, tile_id_to)
            # print hbase_response
            # if len(hbase_response) != 0:
            end = time.time()
            # print "query_time" + ": " + str(end - start)


            # q_time.append(end - start)


            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()


            self.wfile.write(hbase_response)




            # if len(q_time) == 200:
            #     print "hundred"
            #     plt.plot(range(len(q_time)), q_time)
            #     plt.ylabel('hbase query time')
            #     plt.axis([1, 200, 0, 3])
            #     print float(sum(q_time)) / len(q_time)
            #     plt.show()

            return

        if url.path == '/time_series':
            query_components = parse_qs(urlparse(self.path).query)
            level = query_components["level"][0]
            bounds = query_components["bounds"][0]
            bounds = bounds.split(",")
            time_from = transToStamp( query_components["time_from"][0] )
            time_to = transToStamp( query_components["time_to"][0])


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

            #print res

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(res)

            return


if __name__ == '__main__':
    jpype.startJVM(jpype.getDefaultJVMPath(), "-ea ", "-Djava.class.path=%s" % ('/tmp/runClient2.jar'))
    jpype.attachThreadToJVM()
    coprocessor = jpype.JClass("com.hbase.main.MainEntrance")
    cp = coprocessor()

    httpd = ThreadedHTTPServer((HOST_IP, PORT), myHandler)
    print "serving at port", PORT
    httpd.serve_forever()




