import mercantile
import redis
import time
import lua_query

def quadkey_to_num(qk):
    number = 0
    for i, digit in enumerate(qk):
        number  |= int(digit)
        if i != len(qk)-1:
            number = number << 2
    return number

if __name__ == '__main__':
    r = redis.StrictRedis(host='192.168.0.18', port=6379, db=0)
    pl = r.pipeline()
    tile_query = r.register_script(lua_query.lua_script_2)

    quad_key = mercantile.quadkey(1206*256, 1539*256, 20)
    lnglat = mercantile.ul(1206, 1539, 12)
    print quad_key
    print lnglat
    num = quadkey_to_num(quad_key)
    print num
    start = time.time()

    res = tile_query(keys=[20,quad_key,num,8],args=[0,1000])
    #pl.zrangebyscore(20,241677762560,241677822560)
    #res = pl.execute()
    print len(res)
    end = time.time()

    print "time cost" + ": " + str(end - start)
    #print (response)
    # plt.plot(range(1,101), q_times)
    # plt.ylabel('redis query time')
    # plt.axis([1, 100, 0, 0.5])
    # plt.show()

    #a = sum(results)
    #print a