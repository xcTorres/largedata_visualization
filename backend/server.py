from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
from urlparse import urlparse,parse_qs
import datetime
import jpype
import matplotlib.pyplot as plt
import happybase
import time
import mercantile



HOST_IP = ''
PORT = 9010

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

# class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
#     """Handle requests in a separate thread."""
#     pass



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


            # if not  jpype.isThreadAttachedToJVM():
            # jpype.attachThreadToJVM()

            coprocessor = jpype.JClass("com.hbase.main.MainEntrance")
            cp = coprocessor()

            # hbase_response =cp.mutiSum("tiles", tile_id_from, tile_id_to)
            # hbase_response =cp.mutiSum("brightkite", tile_id_from, tile_id_to)
            hbase_response =cp.mutiSum("crime", tile_id_from, tile_id_to)
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
            time_to = transToStamp( query_components["time_to"][0] )

            tiles = mercantile.tiles(float(bounds[0]),float(bounds[1]),float(bounds[2]), \
                                     float(bounds[3]), [int(level), ])

            tile_numbers = []
            for tile in list(tiles):
                t_quadkey = mercantile.quadkey(tile)
                t_num = quadkey_to_num(t_quadkey)
                tile_numbers.append(t_num)

            tile_numbers = ' '.join(str(x) for x in tile_numbers)
            print tile_numbers
            print time_from
            print time_to

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()


            self.wfile.write(tile_numbers)

if __name__ == '__main__':
    jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % ('/tmp/runClient2.jar'))


    httpd = HTTPServer((HOST_IP, PORT), myHandler)
    print "serving at port", PORT
    httpd.serve_forever()



