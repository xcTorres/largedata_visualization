package com.hbase.coprocessor;

import java.util.ArrayList;
import  java.util.List;

public class DateCal {

    private static List<String> timeCol = new ArrayList<String>();

    public DateCal(){

    }

    public static List<String> Calculate(String date1, String date2){

        int[] bottom = DateSplit(date1);
        int[] up = DateSplit(date2);

        //start time == end time
        if (date1.equals(date2) || (bottom[0] == up[0] && bottom[1] == up[1] && up[2] - bottom[2] == 1)){
            timeCol.add("d" + bottom[0] + "-" + bottom[1] + "-" + bottom[2]);
            return timeCol;
        }

        //calculate months between two dates
        int monthSpace = DateCal.monthBetween(up[0] - bottom[0],bottom[1], up[1]) - 1;

        if(monthSpace < 0)
            timeCol.add("d" + bottom[0] + "-" + bottom[1] + "-" + bottom[2] + "_" + (up[2] - 1));  //two dates in the same month
        else
            calDateSpace(bottom, up, monthSpace);  //in different months

        return timeCol;
    }

    //calculate the date delta
    /*public static int deltaDayCal(int[] date,int base){

        int delta = 0;
        int[] mSum = {0,31,59,90,120,151,181,212,243,273,304,334};

        if (date[0] >= base)
            delta = (date[0] - base) * 365 + mSum[date[1] - 1] + date[2];
        else
            delta = deltaDayCal(date,date[0]) - ((base - date[0]) * 365 + 1);

        if ((date[0] % 4 == 0 && date[0] % 100 != 0 || date[0] % 400 == 0) && date[1] > 2)
            delta += 1;

        return delta;
    }

    private static int deltaMonthCal(int year, int month){

        int delta = 0;

        if (year >= 2016)
            delta = (year - 2016) * 12 + month;
        else
            delta = -1 * (12 - month + 1 +(2016 - year - 1) * 12);

        return delta;
    }*/

    private static void calDateSpace(int[] bottom, int[] up, int monthSpace){

        if(monthSpace >= 11)
        {
            if(bottom[1] + bottom[2] == 2)
            {
                for(int a = 0; a <= up[0] - bottom[0] - 1; a++)
                    timeCol.add("y" + (bottom[0] + a));
            }
            else if(up[0] - bottom[0] > 1)
            {
                for(int b = 1; b < up[0] - bottom[0]; b++)
                    timeCol.add("y" + (bottom[0] + b));
            }

            if(up[1] != 1)
            {
                for(int j = 1; j < up[1]; j++)
                    timeCol.add("m" + up[0] + "-" + j);
            }

            if(bottom[1] != 12 && bottom[1] + bottom[2] != 2)
            {
                for(int k = bottom[1] + 1; k <= 12; k++)
                    timeCol.add("m" + bottom[0] + "-" + k);
            }
        }
        else {
            for(int i = 1; i <= monthSpace; i++)
            {
                int m = bottom[1] + i;
                if(m % 12 == 0)
                    timeCol.add("m" + (bottom[0] + m / 12 - 1) + "-" + 12);
                else
                    timeCol.add("m" + (bottom[0] + m / 12) + "-" + m % 12);
            }
        }

        if(up[2] != 1)
            timeCol.add("d" + up[0] + "-" + up[1] + "-" + "1_" + (up[2] - 1));

        if(bottom[2] == 1)
        {
            if (bottom[1] == 1 && monthSpace >= 11);
            else
                timeCol.add("m" + bottom[0] + "-" + bottom[1]);
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

            timeCol.add("d" + bottom[0] + "-" + bottom[1] + "-" + bottom[2] + "_" + days);
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