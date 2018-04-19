package com.hbase.client;

import java.io.IOException;
import java.util.*;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.HConnection;
import org.apache.hadoop.hbase.client.HConnectionManager;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.HTableInterface;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.coprocessor.Batch;
import org.apache.hadoop.hbase.ipc.BlockingRpcCallback;
import org.apache.hadoop.hbase.ipc.CoprocessorRpcChannel;
import org.apache.hadoop.hbase.util.Bytes;
import org.json.JSONException;
import org.json.JSONObject;

import com.google.protobuf.ServiceException;
import com.hbase.protoc.SpatialAgg.SpatialAggRequest;
import com.hbase.protoc.SpatialAgg.SpatialAggResponse;
import com.hbase.protoc.SpatialAgg.SpatialAggService;
import com.hbase.protoc.SpatialAgg.SumMatrix;
import com.hbase.protoc.TemporalAgg.*;
import com.hbase.protoc.TemporalAgg.TemporalAggResponse.TimeMap;

public class MainEntrance {

    static Configuration conf = null;
    static HConnection connection = null;
    public MainEntrance() throws IOException {

        conf = HBaseConfiguration.create();
        connection = HConnectionManager.createConnection(conf);
    }

    public static void main(String[] args) throws Exception {

        /*long t1 = 0, t2 = 0;

        try {
        	t1 = System.currentTimeMillis();
        	conf = HBaseConfiguration.create();
            connection = HConnectionManager.createConnection(conf);
            
            JSONObject json = timeSeriesSumBySingleRegion("nycTaxi", "15:236013312 15:236013357 15:236013370", "2015-03-01", "2015-03-10");

            //JSONObject json = spatialSumBySingleRegion("nycTaxi","15:236012899","2015-01-01","2015-06-01");
            t2 = System.currentTimeMillis();
            System.out.println(json.toString());
            
            //get("nycTaxi", "15:236012899");
            
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        System.out.println(t2 - t1);*/
    }
    
    public JSONObject spatialSumBySingleRegion(String tableName, String rowkey,
    		String starttime, String endtime) throws IOException {
    	
    	HTableInterface table = connection.getTable(tableName);
    	
    	
    	JSONObject result = new JSONObject();
    	List<Integer> reList = null;
    	
    	CoprocessorRpcChannel channel = table.coprocessorService(rowkey.getBytes());
    	SpatialAggService.BlockingInterface service = SpatialAggService.newBlockingStub(channel);
    	
    	final SpatialAggRequest request = SpatialAggRequest.newBuilder()
							                .setRowKey(rowkey)
							                .setStartTime(starttime)
							                .setEndTime(endtime).build();
    	
    	try {
			SpatialAggResponse response = service.getSpatialAgg(null, request);
			List<SumMatrix> res =response.getSumList();
			
			reList = res.get(0).getArrayList();
			
			for (int i = 0; i < reList.size(); i++) {
                if (reList.get(i) == 0)
                    continue;
                result.put(String.valueOf(i), reList.get(i));
            }
			
		} catch (ServiceException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}finally {
			table.close();
		}
    	
    	return result;
    			 
	}
    
    
    public static JSONObject spatialSum(String tabName,String rowkey, String starttime, String endtime) throws IOException {
        
    	//TableName tableName = TableName.valueOf(tabName);
        //HTable table = new HTable(conf, tableName);
        HTableInterface table = connection.getTable(tabName);

       
        List<Integer> reList = null;
        JSONObject result = new JSONObject();
        System.out.println(starttime+ " "+ endtime);
        final SpatialAggRequest request = SpatialAggRequest.newBuilder()
                                            .setRowKey(rowkey)
                                            .setStartTime(starttime)
                                            .setEndTime(endtime).build();

        try {
            Map<byte[], List<SumMatrix>> res = table.coprocessorService(SpatialAggService.class, null, null,
                    new Batch.Call<SpatialAggService, List<SumMatrix>>() {

                        @Override
                        public List<SumMatrix> call(SpatialAggService agg) throws IOException {
                            // TODO Auto-generated method stub
                            BlockingRpcCallback<SpatialAggResponse> rpcCallback = new BlockingRpcCallback<SpatialAggResponse>();
                            agg.getSpatialAgg(null, request, rpcCallback);
                            SpatialAggResponse response = rpcCallback.get();
                            
                            return response.getSumList();
                        }
                    });
            
           /* for (List<SumMatrix> sum : res.values()){
                
                reList = new ArrayList<Integer>(sum.get(0).getArrayList());
                break;
            }*/
            for (List<SumMatrix> sum : res.values()) {
				for (int i = 0; i < sum.size(); i++) {
					if (reList == null) {
						reList = new ArrayList(sum.get(i).getArrayList());
					}else {
						List<Integer> r = new ArrayList(sum.get(i).getArrayList());
						for (int j = 0; j < reList.size(); j++) {
							reList.set(j, reList.get(j) + r.get(j));
						}
					}
				}
			}



            for (int i = 0; i < reList.size(); i++) {
                if (reList.get(i) == 0)
                    continue;
                result.put(String.valueOf(i), reList.get(i));
            }

        } catch (Exception e) {
            e.printStackTrace();
        } catch (Throwable e) {
            e.printStackTrace();
        }finally {
            table.close();
        }

        return result;
    }

    public static JSONObject timeSeriesSum(String tabName,String tilesNum,String starttime,String endtime) throws IOException {

        //TableName tableName = TableName.valueOf(tabName);
        //HTable table = new HTable(conf, tableName);
        HTableInterface table = connection.getTable(tabName);

        Map<String,Long> map = new HashMap<String, Long>();
        JSONObject result = new JSONObject();


        final TemporalAggRequest request = TemporalAggRequest.newBuilder()
                                            .setTileNumbers(tilesNum)
                                            .setStartTime(starttime)
                                            .setEndTime(endtime).build();


        try {
            Map<byte[], List<TimeMap>> res = table.coprocessorService(TemporalAggService.class, null, null,
                    new Batch.Call<TemporalAggService, List<TimeMap>>() {

                        @Override
                        public List<TimeMap> call(TemporalAggService agg) throws IOException {
                            // TODO Auto-generated method stub
                            BlockingRpcCallback<TemporalAggResponse> rpcCallback = new BlockingRpcCallback<TemporalAggResponse>();
                            agg.getTemporalAgg(null, request, rpcCallback);
                            TemporalAggResponse response = rpcCallback.get();

                            return response.getTimeMapList();
                        }
                    });


            for (List<TimeMap> tm : res.values()) {
                for (int i = 0; i < tm.size(); i++) {
                    String k = tm.get(i).getKey();
                    long v = tm.get(i).getValue();
                    if(!map.containsKey(k))
                        map.put(k, v);
                    else
                        map.put(k, map.get(k) + v);
                }
            }



            Set<String> key_arr =  map.keySet();

            for (String key : key_arr)
            {
                //System.out.println(String.valueOf(key) + " " +map.get(String.valueOf(key)) );
                result.put(String.valueOf(key), map.get(String.valueOf(key)));
            }

        } catch (Exception e) {
            e.printStackTrace();
        }catch (Throwable e) {
            e.printStackTrace();
        }finally {
            table.close();
        }

        return result;

    }
    
    public JSONObject timeSeriesSumBySingleRegion(String tabName,String rkArray,String starttime,String endtime) throws IOException {
    	
    	HTableInterface table = connection.getTable(tabName);
    	
    	JSONObject result = new JSONObject();
    	Map<String,Long> map = new HashMap<String, Long>();
    	
    	String[] rk = rkArray.split(" ");
    	CoprocessorRpcChannel channel = null;
    	TemporalAggService.BlockingInterface service = null;
    	TemporalAggRequest request = null;
    	TemporalAggResponse response = null;
    	
    	try {
    		
	    	for(int i = 0; i < rk.length; i++)
	    	{
	    		channel = table.coprocessorService(rk[i].getBytes());
	    		service = TemporalAggService.newBlockingStub(channel);
	    		
	    		request = TemporalAggRequest.newBuilder()
	                    .setTileNumbers(rk[i])
	                    .setStartTime(starttime)
	                    .setEndTime(endtime).build();
	    		response = service.getTemporalAgg(null, request);
	    		List<TimeMap> res = response.getTimeMapList();
	    		
	    		
                for (int j = 0; j < res.size(); j++) {
                	
                    String k = res.get(j).getKey();
                    long v = res.get(j).getValue();
                    
                    if(!map.containsKey(k))
                        map.put(k, v);
                    else
                        map.put(k, map.get(k) + v);
                }
                
	    	}
	    	
	    	Set<String> key_arr =  map.keySet();
	    	for (String key : key_arr)
                result.put(String.valueOf(key), map.get(String.valueOf(key)));
		
    	} catch (ServiceException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}finally {
			table.close();
		}
    	
    	return result;
    	
    }
    
    
    private static void get(String tablename,String row) throws Exception{
		
		//HTable table = new HTable(conf, tablename);
		
		HTableInterface table = connection.getTable(tablename);
		Get get = new Get(Bytes.toBytes(row));
		Result result = table.get(get);
		System.out.println("Get: " + result);
	}

}
