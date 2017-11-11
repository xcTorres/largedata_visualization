package com.hbase.coprocessor;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.Coprocessor;
import org.apache.hadoop.hbase.CoprocessorEnvironment;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.coprocessor.CoprocessorException;
import org.apache.hadoop.hbase.coprocessor.CoprocessorService;
import org.apache.hadoop.hbase.coprocessor.RegionCoprocessorEnvironment;
import org.apache.hadoop.hbase.protobuf.ResponseConverter;
import org.apache.hadoop.hbase.regionserver.InternalScanner;
import org.apache.hadoop.hbase.util.Bytes;

import com.google.protobuf.RpcCallback;
import com.google.protobuf.RpcController;
import com.google.protobuf.Service;
import com.hbase.protoc.MatrixColAgg.MatrixColAggRequest;
import com.hbase.protoc.MatrixColAgg.MatrixColAggResponse;
import com.hbase.protoc.MatrixColAgg.MatrixColAggService;
import com.hbase.protoc.MatrixColAgg.SumMatrix;

public class MatColAgg extends MatrixColAggService implements Coprocessor,CoprocessorService{

	private RegionCoprocessorEnvironment env;
	
	private static List<String> col = new ArrayList<String>(){{
		add("all");
		}};
		
	@Override
	public Service getService() {
		// TODO Auto-generated method stub
		return this;
	}

	@Override
	public void start(CoprocessorEnvironment arg0) throws IOException {
		// TODO Auto-generated method stub
		if (arg0 instanceof RegionCoprocessorEnvironment) {
			this.env = (RegionCoprocessorEnvironment) arg0;
		}else
			throw new CoprocessorException("Must be loaded on a table region!");
	}

	@Override
	public void stop(CoprocessorEnvironment arg0) throws IOException {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void getMatrixColAgg(RpcController controller, MatrixColAggRequest request,
			RpcCallback<MatrixColAggResponse> done) {
		// TODO Auto-generated method stub
		Scan scan = new Scan();
		scan.addColumn(Bytes.toBytes("cfarray"), Bytes.toBytes(col.get(0)));
		
		scan.setStartRow(Bytes.toBytes(request.getStartKey()));
		scan.setStopRow(Bytes.toBytes(request.getEndKey()));
		
		MatrixColAggResponse response = null;
		InternalScanner scanner = null;
		
		try {
			scanner = env.getRegion().getScanner(scan);
			List<Cell> result = new ArrayList<Cell>();
			boolean bl = false;
			List<Integer> ll = new ArrayList<Integer>();
			for (int i = 0; i < 65536; i++) {
				ll.add(0);
			}
			
			do {
				bl = scanner.next(result);
				for (int i = 0; i < col.size(); i++) {
					String c = col.get(i);
					for (Cell cell : result) {
						if (c.equals(Bytes.toString(cell.getQualifier()))) {
							byte[] val = cell.getValue();
							if (val == null || val.length == 0); 
							else {
								MatrixAgg(ll, val);
							}	
							break;
						}
					}
				}
				result.clear();
			} while (bl);
			
			
			SumMatrix[] sum = {SumMatrix.newBuilder().addAllArray(ll).build()};
			List<SumMatrix> lst = Arrays.asList(sum);
			response = MatrixColAggResponse.newBuilder().addAllSum(lst).build();
			
		} catch (IOException e) {
			ResponseConverter.setControllerException(controller, e);
		}finally {
			try {
				scanner.close();
			} catch (IOException e) {
			}
		}
		done.run(response);
	}

	
	private void MatrixAgg(List<Integer> l, byte[] val) {
		
		String[] str = new String(val).split(" ");
		for (String s : str) {
			int index = Integer.parseInt(s.split(":")[0]);
			int value = Integer.parseInt(s.split(":")[1]);
			l.set(index, l.get(index) + value);
		}
	}
}
