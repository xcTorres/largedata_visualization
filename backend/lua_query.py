import redis
import time
import json
import mercantile

lua_script = """
    local function tile(x,y,zoom)
        local t = {}
        t["x"] = x
        t["y"] = y
        t["zoom"] = zoom
        
        return t
    end
        
    local function split(id)
        local zoom, x, y = id:match("([^,]+)_([^,]+)_([^,]+)")
        return zoom,x,y
    end
        
        
     local function get_children(x,y,zoom)
        
        local x = tonumber(x)
        local y = tonumber(y)
        local zoom = tonumber(zoom)
        
        local children = {}
        children[1] = tile(x*2,y*2,zoom+1)
        children[2] = tile(x*2+1,y*2,zoom+1)
        children[3] = tile(x*2+1,y*2+1,zoom+1)
        children[4] = tile(x*2,y*2+1,zoom+1)
        
        return children
    end
        
    table.reduce = function (list, fn)
        local acc
        for k, v in ipairs(list) do
            if v == false then
                v = 0
            end
            if 1 == k then
                acc = v
            else
                acc = fn(acc, v)
            end
        end
        return acc
    end
        
        
    local pixels = {}
    local origin = {}
    local query_tiles
    query_tiles = function(t,time_range,level)
        
        if (level >= 8) then
            local id = tostring(t.zoom)..'_'..tostring(t.x)..'_'..tostring(t.y)
            local redis_res = redis.call("hmget",id,unpack(time_range))
                
            local sum = table.reduce(
                redis_res,
                function (a, b)
                    return a + b
                end
            )
                
            if sum ~= 0 then
                local current_zoom, current_x, current_y = split( id )
                local item  = {}
                item['x'] = current_x - origin['x']
                item['y'] = current_y - origin['y']
                item['v'] = sum
                table.insert(pixels,item)
            end
        else
            if level == 0 then
                origin['x'] = t.x * math.pow(2,8)
                origin['y'] = t.y * math.pow(2,8)
            end
                
            local tile_id = tostring(t.zoom)..'_'..tostring(t.x)..'_'..tostring(t.y)
            if redis.call("EXISTS", tile_id) == 1 then
                local children = get_children(t.x,t.y,t.zoom)
                query_tiles(children[1],time_range,level+1)
                query_tiles(children[2],time_range,level+1)
                query_tiles(children[3],time_range,level+1)
                query_tiles(children[4],time_range,level+1)
            else
            end
        
        end
        
    end
        
    --local from = redis.call("TIME")
    local current_zoom, current_x, current_y = split( KEYS[1] )
    local time_range = loadstring("return "..KEYS[2])()
        
    local current_node  = tile( current_x, current_y, current_zoom )
    query_tiles(current_node,time_range,0)
        
    local json_res = cjson.encode(pixels)
        
    --local to = redis.call("TIME")
    --local delta = (to[2]-from[2])
    --return (delta)
        
    return json_res
    
    """