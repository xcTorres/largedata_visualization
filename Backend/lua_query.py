import redis
import time
import json
import mercantile

lua_script_2 = """
    
    local function quadkey_to_xy(quadkey,level)

        local xtile,ytile = 0,0
        local reverse = string.reverse(quadkey)
    
        for i = 1,string.len(reverse) do
            local mask = bit.lshift(1,i-1)
            local digit = reverse:sub(i,i)
    
            if digit == '1' then
    
                xtile = bit.bor( xtile, mask )
    
            elseif digit == '2' then
    
                ytile = bit.bor( ytile, mask )
    
            elseif digit == '3' then
    
                xtile = bit.bor( xtile, mask )
                ytile = bit.bor( ytile, mask )
            end
        end
    
        return xtile,ytile

    end
    
    local function time_lu_bounds(time_series,time_from,time_to)
        local len = #time_series
        local lu_index = {}
              
        local iStart,iEnd,iMid,Mid_value = 2,len,2,0
        while iStart <= iEnd do
            iMid = math.floor( (iStart+iEnd)/2 )
            Mid_value =  tonumber( time_series[iMid] )
            if  time_from <= Mid_value then
                iEnd = iMid - 1
            else
                iStart = iMid + 1
            end
        end
        if iStart == len+1 then
            return false
        end
        lu_index[1] = iStart-2
        
        iStart,iEnd,iMid,Mid_value = 2,len,2,0
        while iStart <= iEnd do
            iMid = math.floor( (iStart+iEnd)/2 )
            Mid_value =  tonumber( time_series[iMid] )
            if  time_to < Mid_value then
                iEnd = iMid - 1
            else
                iStart = iMid + 1
            end
        end
        if iEnd == 1 then
            return false
        end
        lu_index[2] = iEnd-2
        
        return lu_index
    end
    
    local function query(level,quad_num,resolution)
    
        local range = math.pow(2,resolution*2)
        local res =  redis.call("zrangebyscore",level,quad_num,quad_num+range-1)
        return res
    end
    
    local level = KEYS[1]
    local quad_key = KEYS[2]
    local quad_num = KEYS[3]
    local resolution = KEYS[4]
    local time_from = tonumber(ARGV[1])
    local time_to = tonumber(ARGV[2])
    
    local time_series_list = query(level,quad_num,resolution)   
    local pixels = {}
    --for index,value in pairs(time_series_list) do
        --local time_str ='{'..value..'}'
        --local time_series = loadstring("return "..time_str)()
        --table.insert(pixels,time_series)
    --end
    return time_series_list
"""