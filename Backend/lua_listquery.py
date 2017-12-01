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
    
    
    local function lu_bounds(id,from,to)
        local len = redis.call("llen",id)
        local lu_index = {}
        
        local iStart,iEnd,iMid,Mid_value = 0,len-1,0,0
        while iStart <= iEnd do
            iMid = math.floor( (iStart+iEnd)/2 )
            Mid_value =  tonumber( redis.call("lindex",id,iMid) )
            if  from <= Mid_value then
                iEnd = iMid - 1
            else
                iStart = iMid + 1
            end
        end
        if iStart == len then
            return false
        end
        lu_index[1] = iStart
        
        
        iStart,iEnd,iMid,Mid_value = 0,len-1,0,0
        while iStart <= iEnd do
            iMid = math.floor( (iStart+iEnd)/2 )
            Mid_value =  tonumber( redis.call("lindex",id,iMid) )
            if  to < Mid_value then
                iEnd = iMid - 1
            else
                iStart = iMid + 1
            end
        end
        if iEnd == -1 then
            return false
        end
        lu_index[2] = iEnd
        
        return lu_index
    end
        
        
    local pixels = {}
    local origin = {}
    local query_tiles
    query_tiles = function(t,time_range,level)
        
        if (level >= 7) then
            local id = tostring(t.zoom)..'_'..tostring(t.x)..'_'..tostring(t.y)
            local tile_v = "{"..id.."}"..":v"
            local tile_t = "{"..id.."}"..":t"
            local lu = lu_bounds(tile_t,time_range[1],time_range[2])
            
            if lu ~= false then
                local agg_value
                if lu[1] ~= lu[2] then
                    local agg_from = redis.call("lindex",tile_v,lu[1])
                    local agg_to = redis.call("lindex",tile_v,lu[2])
                    agg_value = tonumber(agg_to)-tonumber(agg_from)
                else
                    local agg_from = redis.call("lindex",tile_v,lu[1])
                    agg_value = tonumber(agg_from)
                end
                if agg_value > 0 then
                    local item  = {}
                    item['x'] = (t.x - origin['x'])*2
                    item['y'] = (t.y - origin['y'])*2
                    item['v'] = agg_value
                    table.insert(pixels,item)
                end
            end
        else
            if level == 0 then
                origin['x'] = t.x * math.pow(2,7)
                origin['y'] = t.y * math.pow(2,7)
            end
                
            local tile_id = tostring(t.zoom)..'_'..tostring(t.x)..'_'..tostring(t.y)
            tile_id = "{"..tile_id.."}"..":t"
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
    
    --local tile_v = "{"..KEYS[1].."}"..":v"
    --local tile_t = "{"..KEYS[1].."}"..":t"
    --local lu = lu_bounds(tile_t,1,24)
    --return lu[2]
      
    local json_res = cjson.encode(pixels)
        
        
    return json_res
    
    """