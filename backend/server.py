import SimpleHTTPServer
import SocketServer
from urlparse import urlparse,parse_qs
import json
import time
import redis
import lua_query

HOST_IP = ''
PORT = 9001

r = redis.StrictRedis(host='192.168.0.18', port=6379, db=0)
tile_query = r.register_script(lua_query.lua_script)


class myHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)

        if url.path == '/tile':
            query_components = parse_qs(urlparse(self.path).query)
            level = query_components["level"][0]
            x = query_components["x"][0]
            y = query_components["y"][0]

            start = time.time()

            tile_id = level+'_'+x+'_'+y
            print tile_id
            response = tile_query(keys=[tile_id, "{'all'}"])
            response = json.loads(response)

            end = time.time()
            print "query_time" + ": " + str(end - start)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # print result_list

            self.wfile.write(json.dumps(response))
            return

if __name__ == '__main__':

    httpd = SocketServer.TCPServer((HOST_IP, PORT), myHandler)
    print "serving at port", PORT
    httpd.serve_forever()
