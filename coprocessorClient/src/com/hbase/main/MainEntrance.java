package com.hbase.main;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.coprocessor.Batch;
import org.apache.hadoop.hbase.ipc.BlockingRpcCallback;
import org.json.JSONArray;
import org.json.JSONObject;

import com.hbase.protoc.MatrixColAgg.MatrixColAggRequest;
import com.hbase.protoc.MatrixColAgg.MatrixColAggResponse;
import com.hbase.protoc.MatrixColAgg.MatrixColAggService;
import com.hbase.protoc.MatrixColAgg.SumMatrix;

public class MainEntrance {

	static Configuration conf = null;
	
	public MainEntrance() {
		
		conf = HBaseConfiguration.create();
	}
	
	
	public static void main(String[] args) {
		
	}

	
	public JSONObject mutiSum(String tabName) throws IOException {
		return mutiSum(tabName,"","");
	}
	
	public JSONObject mutiSum(String tabName,String startkey,String endkey) throws IOException {
		TableName tableName = TableName.valueOf(tabName);
		HTable table = new HTable(conf, tableName);
				
		List<Integer> reList = null;
		JSONObject result = new JSONObject();
		
		final MatrixColAggRequest request = MatrixColAggRequest.newBuilder().setStartKey(startkey).setEndKey(endkey).build();
		
		try {	
			Map<byte[], List<SumMatrix>> res = table.coprocessorService(MatrixColAggService.class, null, null, 
					new Batch.Call<MatrixColAggService, List<SumMatrix>>() {

						@Override
						public List<SumMatrix> call(MatrixColAggService agg) throws IOException {
							// TODO Auto-generated method stub
							BlockingRpcCallback<MatrixColAggResponse> rpcCallback = new BlockingRpcCallback<MatrixColAggResponse>();
							agg.getMatrixColAgg(null, request, rpcCallback);
							MatrixColAggResponse response = rpcCallback.get();
							
							return response.getSumList();
						}
					});
							
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
		}
		
		return result;
	}
	
}
