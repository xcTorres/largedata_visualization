import happybase
import time

connection = happybase.Connection(host='192.168.0.17')
# before first use:
connection.open()

#filter="RowFilter(=,'14750834:2016-06-26_2')
# heat = {
#     'cfarray': dict(),
# }
# connection.create_table('brightkite', heat)
# print(connection.tables())

start = time.time()
table  = connection.table('crime')
with table.batch(batch_size=1000) as b:
    with open('/home/xc/brightkite_result.txt', 'r') as f:
        line_count = 0
        for line in f:
            item = eval(line)
            tile_id  = item[0]

            result = []
            sum = 0
            for ele in item[1]:

                k = ele[0]
                v = ele[1]
                sum += v
                kv = str(k)+':'+str(v)

                result.append(kv)

            result = ' '.join(str(x) for x in result)

            b.put(tile_id, {
                b'cfarray:all': (result) ,
                b'cfarray:sum': str(sum)
            })
            line_count += 1

            if line_count % 1000 == 0:
                #break
                print  line_count

# for key,data in table.scan(filter="PageFilter(10)"):
#     print data
#
end = time.time()
print str(end-start)