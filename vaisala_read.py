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

"""can be used to write to a differnt file whenever weather station reader is turned on


def check_if_file_exists(base_name):
    file_number = 0
    for file in os.listdir():
        if file == base_name + "_" + str(file_number).zfill(2) + ".txt":
            file_number = file_number + 1
            file_number = str(file_number).zfill(2)
    return base_name + file_number
"""


def create_log_file(id_num=""):
    global local_file, raw_data, header, base_name
    out_dir = 'C:/Users/Administrator/Desktop/em-27_aux_scripts/75_met//' #output directory for files J
    base_name = (out_dir + dt.date.today().strftime("%Y%m%d") + "_" + str(id_num)) #full base filename J
    raw_data = open(base_name + "_raw_strings.txt", mode="a")
    header = ("UTCDate,UTCTime,wdmin(D),wdavg(D),wdmax(D),wsmin(ms-1)," +
              "wsavg(ms-1)," +
              "wsmax(ms-1),Tout,RH,Pout,rainaccum(mm)," +
              "raindur(s),rainintensity(mmh-1),hailaccum(hitscm-2), " +
              "haildur(s),hailintensity(hitscm-2h-1)," +
              "rainpkintensity(mmh-1)," +
              "hailpkintensiy(hitscm-2)" + "\n"
              )
    try:
        local_file_header = open(base_name + ".txt", mode="r").readlines()[0]
        local_file = open(base_name + ".txt", mode="a")
        return
    except FileNotFoundError:
        local_file = open(base_name + ".txt", mode="a")
        local_file.write(header)
        local_file.flush()
        return
    return


def interprate_vaisala_string(ser, log_file, id_num):
    global stop_event, base_name
    data_dict = {"R1": slice(2, 8), "R2": slice(8, 11),
                 "R3": slice(11, 19)
                 }
    r2_ffill = [np.nan] * 3
    while not stop_event.is_set():
        """this loop reads the data from the vaisala and assocaites it with its
           correct postiion using data dict and fills in approiate nans
           in data lst
        """
        
        data_lst = [np.nan] * 19
        x = str(ser.readline())[3:-3]
        

        sentence = x[:-2].split(",")
        """these read from the serial port and remove the ''b' at the start of
           the byte string and removes the \r\n at the end of it
        """
        measurement_datetime= dt.datetime.now(utc)
        if x != "":
            raw_data.write(str(measurement_datetime) + "," + x[0:-2] + "\n")
            raw_data.flush()
        measurement_time = measurement_datetime.strftime("%H:%M:%S.%f")
        measurement_date = measurement_datetime.strftime("%Y/%m/%d")
        """assocaite a tme with the measurement"""
        key = sentence[0]
        """key is used to find correct nans to rewrite using data dict"""
      
        if key != (""):
            data = [var[3:-1] for var in sentence[1:]]
          #  if key == "R2":
           #     r2_ffill = data
            #data_lst[data_dict["R2"]] = r2_ffill
            """removes units from end of varaibbles"""
            data_lst[0] = measurement_date
            data_lst[1] = measurement_time
            """insert measurement time"""
            try:
                data_lst[data_dict[key]] = data
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
        #if r2_ffill == [np.nan]*3:
         #   continue
        else:
            if len(data_lst) == 19:
                print(str(id_num) + " " + " data: \n" + data_str)
                local_file.write(data_str)
                local_file.flush()
            continue
            """if data lst has any data in it we write to the local
               and remote files and save them
            """
    print("Closing open serial ports and files")
    local_file.close()
    raw_data.close()
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
    infile2 = []
    for l in infile:
        try:
            infile2.append(l[0])
        except KeyboardInterrupt:
            raise
        except:
            infile2.append("")
    infile = infile2
    stop_event = threading.Event()
    """above processes infile and handles missing lines"""
    loc_nat, loc_sue = (infile[0], infile[1])
    if (loc_nat != "" and loc_sue != ""):
        print("Both Vaisalas connected")
        """define first raeading thread"""

        def vais1():
            ser1 = serial.Serial(loc_nat, baudrate=19200, timeout=1)
            id_num = "76_nat"
            file1 = create_log_file(id_num)
            interprate_vaisala_string(ser1, file1, id_num)
        t1 = threading.Thread(target=vais1)
        """define second raeading thread"""

        def vais2():
            ser2 = serial.Serial(loc_sue, baudrate=19200, timeout=1)
            id_num = "75_sus"
            file2 = create_log_file(id_num)
            interprate_vaisala_string(ser2, file2, id_num)
        t2 = threading.Thread(target=vais2)
        t1.setDaemon(True)
        t2.setDaemon(True)
        t1.start()
        t2.start()
    elif (loc_nat != "" and loc_sue == ""):
        print("75_sus not connected log for only 76_nat only")

        def vais1():
            ser1 = serial.Serial(loc_nat, baudrate=19200, timeout=1)
            id_num = "76_nat"
            file1 = create_log_file(id_num)
            interprate_vaisala_string(ser1, file1, id_num)
        t1 = threading.Thread(target=vais1)
        t1.setDaemon(True)
        t1.start()
    elif (loc_nat == "" and loc_sue != ""):
        print("76_nat not connected log for only 75_sus only")

        def vais1():
            ser1 = serial.Serial(loc_sue, baudrate=19200, timeout=1)
            id_num = "75_sus"
            file1 = create_log_file(id_num)
            interprate_vaisala_string(ser1, file1, id_num)
        t1 = threading.Thread(target=vais1)
        t1.setDaemon(True)
        t1.start()
    else:
        print("No Vaisalas are connected")
        return


def stop():
    stop_event.set()



if __name__ == "__main__":
    print("Please unsure you exit the reader using the stop() function." +
          " This runs the post-processing required for the data to be read into EGI"
          )
    main()
