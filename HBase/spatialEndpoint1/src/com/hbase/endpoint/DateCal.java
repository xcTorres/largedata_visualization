package com.hbase.endpoint;

import java.util.ArrayList;
import  java.util.List;

public class DateCal {

    //private static List<String> timeCol = new ArrayList<String>();

    public DateCal(){

    }

    public static List<String> Calculate(String date1, String date2){

    	List<String> timeCol = new ArrayList<String>();
        int[] bottom = DateSplit(date1);
        int[] up = DateSplit(date2);

        //start time == end time
        if (date1.equals(date2) || (bottom[0] == up[0] && bottom[1] == up[1] && up[2] - bottom[2] == 1)){
            timeCol.add(bottom[0] + "-" + (bottom[1] > 9 ? bottom[1] : "0" + bottom[1]) + "-" 
            			+ (bottom[2] > 9 ? bottom[2] : "0" + bottom[2]));
            return timeCol;
        }

        //calculate months between two dates
        int monthSpace = DateCal.monthBetween(up[0] - bottom[0],bottom[1], up[1]) - 1;

        if(monthSpace < 0){
        	for (int i = bottom[2]; i < up[2]; i++) {
        		timeCol.add(bottom[0] + "-" + (bottom[1] > 9 ? bottom[1] : "0" + bottom[1]) + "-" 
            			+ (i > 9 ? i : "0" + i));    //two dates in the same month
			}
        }
        else
            calDateSpace(bottom, up, monthSpace, timeCol);  //in different months

        return timeCol;
    }

    
    private static void calDateSpace(int[] bottom, int[] up, int monthSpace,List<String> timeCol){

        if(monthSpace >= 11)
        {
            if(bottom[1] + bottom[2] == 2)
            {
                for(int a = 0; a <= up[0] - bottom[0] - 1; a++)
                    timeCol.add("" + (bottom[0] + a));
            }
            else if(up[0] - bottom[0] > 1)
            {
                for(int b = 1; b < up[0] - bottom[0]; b++)
                    timeCol.add("" + (bottom[0] + b));
            }

            if(up[1] != 1)
            {
                for(int j = 1; j < up[1]; j++)
                    timeCol.add(up[0] + "-" + (j > 9 ? j : "0" + j));
            }

            if(bottom[1] != 12 && bottom[1] + bottom[2] != 2)
            {
                for(int k = bottom[1] + 1; k <= 12; k++)
                    timeCol.add(bottom[0] + "-" + (k > 9 ? k : "0" + k));
            }
        }
        else {
            for(int i = 1; i <= monthSpace; i++)
            {
                int m = bottom[1] + i;
                if(m % 12 == 0)
                    timeCol.add((bottom[0] + m / 12 - 1) + "-" + 12);
                else
                    timeCol.add((bottom[0] + m / 12) + "-" + (m % 12 > 9 ? m % 12 : "0" + m % 12));
            }
        }

        if(up[2] != 1){
        	for (int i = 1; i < up[2]; i++) {
        		timeCol.add(up[0] + "-" + (up[1] > 9 ? up[1] : "0" + up[1]) + "-"
            				+ (i > 9 ? i : "0" + i));
			}
        }
        
        if(bottom[2] == 1)
        {
            if (bottom[1] == 1 && monthSpace >= 11);
            else
                timeCol.add(bottom[0] + "-" + (bottom[1] > 9 ? bottom[1] : "0" + bottom[1]));
        }
        else {
            int days = 0;
            switch (bottom[1]) {
                case 4:
                case 6:
                case 9:
                case 11:
                    days = 30;
                    break;
                case 1:
                case 3:
                case 5:
                case 7:
                case 8:
                case 10:
                case 12:
                    days = 31;
                    break;
                default:
                    if (bottom[0] % 4 == 0 && bottom[0] % 100 != 0 || bottom[0] % 400 == 0)
                        days = 29;
                    else
                        days = 28;
                    break;
            }

            for (int i = bottom[2]; i <= days; i++) 
            	timeCol.add(bottom[0] + "-" + (bottom[1] > 9 ? bottom[1] : "0" + bottom[1]) + "-" 
            				+ (i > 9 ? i : "0" + i));	
            
        }
    }


    public static int[] DateSplit(String date) {

        return new int[]{Integer.parseInt(date.split("-")[0]),Integer.parseInt(date.split("-")[1]),Integer.parseInt(date.split("-")[2])};
    }


    private static int monthBetween(int yearSpace, int start, int end)
    {
        int result = yearSpace * 12 + end - start;
        return result == 0 ? 0 : Math.abs(result);
    }

}