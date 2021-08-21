#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 11:41:41 2017
@author: sajjan
"""
import serial
import datetime as dt
import numpy as np
import threading
import os
import pytz
import time
import pandas as pd
utc = pytz.timezone("utc")
from serial.tools import list_ports


def create_log_file(id_num=""):
    global local_file, header, base_name
    out_dir = 'C:/Users/Administrator/Desktop/em-27_aux_scripts/vaisala//' #output directory for files J
    base_name = (out_dir + dt.date.today().strftime("%Y%m%d") + "_" + str(id_num)) #full base filename J
    header = ("UTCDate,UTCTime,WDIR,WSPD,Tout,RH,Pout,rainaccum,rainintensity,hailaccum,hailintensityd, ID" +"\n"
              )
    try:
        local_file_header = open(base_name + ".txt", mode="r").readlines()[0]
        local_file = open(base_name + ".txt", mode="a")
        return
    #except FileNotFoundError:
    except IOError:
        local_file = open(base_name + ".txt", mode="a")
        local_file.write(header)
        local_file.flush()
        return
    return


def interprate_vaisala_string(ser, log_file, id_num):
    global stop_event, base_name
    while not stop_event.is_set():
        """this loop reads the data from the vaisala and assocaites it with its
           correct position using data dict and fills in approiate nans
           in data lst
        """
        create_log_file(id_num)
        data_lst = [np.nan] * 12
        x = str(ser.readline())[3:-3]

        sentence = x[:-2].split(",")
        """these read from the serial port and remove the ''b' at the start of
           the byte string and removes the \r\n at the end of it
        """
        measurement_datetime= dt.datetime.now(utc)
        if x != "":
               measurement_time = measurement_datetime.strftime("%H:%M:%S.%f")
               measurement_date = measurement_datetime.strftime("%Y/%m/%d")
        """associate a time with the measurement"""
        """key is used to find correct nans to rewrite using data dict"""
        data = [var[3:-1] for var in sentence[1:]]
        """removes units from end of varaibbles"""
        data_lst[0] = measurement_date
        data_lst[1] = measurement_time
        """insert measurement time"""
        try:
          data_lst[2:12] = data
        except KeyboardInterrupt:
            raise
        except:
            continue
        """rewrite datalst"""
        data_str = str(data_lst)[1:-1] + "\n"
        data_str = "%s" % ",".join(map(str, data_lst)) + "\n"
        if all(v is np.nan for v in data_lst):
            continue
            """if no data in string don't write to file
               and print something saying no data
            """
        else:
            if len(data_lst) == 12:
                #print(str(id_num) + " " + " data: \n", data_str)
                print(data_str)
                local_file.write(data_str)
                local_file.flush()
            continue
            """if data lst has any data in it we write to the local
               and remote files and save them
            """
    print("Closing open serial ports and files")
    local_file.close()
    ser.close()
    print("Interpolating and filling Tout, Pout and RH")

    data = pd.read_csv(base_name + ".txt")
    data["dt"] = [Date + Time for Date, Time in zip(data["UTCDate"], data["UTCTime"])]
    data["dt"] = pd.to_datetime(data["dt"], format="%Y/%m/%d%H:%M:%S.%f")
    data.index = data["dt"]
    del data["dt"]
    data["Tout"] = data["Tout"].interpolate("time").fillna(method="ffill").fillna(method="bfill")
    data["Pout"] = data["Pout"].interpolate("time").fillna(method="ffill").fillna(method="bfill")
    data["RH"] = data["RH"].interpolate("time").fillna(method="ffill").fillna(method="bfill")

    data.index = data["UTCDate"]
    del data["UTCDate"]
    data.to_csv(base_name + "2.txt", float_format="%.1f", na_rep="nan")
    print("Exiting")
    exit()                 



def main():
    """open daemons based on number of vaisala's found"""
    global infile, stop_event
    infile = [l.rsplit() for l in open("vaisala_infile", mode="r").readlines()
              if l[0] != "#"
              ]
    stop_event = threading.Event()
    """above processes infile and handles missing lines"""
    try:
        vaisala = list(list_ports.grep("Vaisala*"))
    except StopIteration:
        print ("No device found")
    loc_nat = vaisala[0][0]
    loc_nat = loc_nat.encode('ascii','replace')

    print("Vaisala COM port is", loc_nat.decode('UTF-8'))

    if (loc_nat != ""):
        ser1 = serial.Serial(loc_nat.decode('UTF-8'), baudrate=19200, timeout=1)
        id_num = "vaisala"
        file1 = create_log_file(id_num)
        interprate_vaisala_string(ser1, file1, id_num)
    else:
        print("No Vaisalas are connected")
        return


def stop():
    stop_event.set()



if __name__ == "__main__":
    print("Please ensure you exit the reader using the exit() function." +
          " This runs the post-processing required for the data to be read into EGI"
          )
    main()
