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
import os.listdir


def check_if_file_exists(base_name):
    file_number = 0
    for file in os.listdir():
        if file == base_name + "_" + str(file_number).zfill(2) + ".txt":
            file_number = file_number + 1
            file_number = str(file_number).zfill(2)
    return base_name + file_number + ".txt"


def create_log_file(id_num=""):
    """this fucntions creates the logging files, one goes to the local
       directory and the other
       goes to Nasrin's dropbox. Name format is
       Vaisalaname_vaisala_data_YYYY-MM-DD_00.txt
    """
    global local_file, remote_file
    date = dt.datetime.now()
    year = str(date.year)
    month = str(date.month)
    day = str(date.day)
    base_name = (str(id_num) + "_vaisala" + "_data" + "_" +
                 year + month + day + "_"
                 )
    file_name = check_if_file_exists(base_name)
    local_file = open(file_name, mode="a")
    remote_file = open(infile[2] + file_name, mode="a")
    header = ("Time, wdmin(D), wdavg(D), wdmax(D), wsmin(ms-1), " +
              "wsavg(ms-1), " +
              "wsmax(ms-1), temp(C), humid(%), press(hPa), rainaccum(mm), " +
              "raindur(s), rainintensity(mm/h), hailaccum(hits/cm2), " +
              "haildur(s), hailintensity(hits/cm2/h), " +
              "rainpkintensity(mm/h), " +
              "hailpkintensiy(hits/cm2), pt100, aux_rain(mm), " +
              "level(V*gain), " +
              "solar_rad(V*gain), heating_temp(C), heating_volt(V)," +
              "supply_volt(V), ref_volt(V)" + "\n"
              )
    local_file.write(header)
    local_file.flush()
    remote_file.write(header)
    remote_file.flush()
    """write headers to both files"""
    return file_name


def interprate_vaisala_string(ser, log_file, id_num):
    data_dict = {"R1": slice(1, 7), "R2": slice(7, 10), "R3": slice(10, 18),
                 "R4": slice(18, 22), "R5": slice(22, None)
                 }
    while True:
        """this loop reads the data from the vaisala and assocaites it with its
           correct postiion using data dict and fills in approiate nans
           in data lst
        """
        data_lst = [np.nan] * 25
        x = str(ser.readline())[3:-3]
        sentence = x[:-2].split(",")
        """these read from the serial port and remove the ''b' at the start of
           the byte string and removes the \r\n at the end of it
        """
        measurement_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        """assocaite a tme with the measurement"""
        key = sentence[0]
        """key is used to find correct nans to rewrite using data dict"""
        if key != (""):
            data = [var[3:-1] for var in sentence[1:]]
            """removes units from end of varaibbles"""
            data_lst[0] = measurement_time
            """insert measurement time"""
            try:
                data_lst[data_dict[key]] = data
            except KeyboardInterrupt:
                raise
            except:
                continue
            """rewrite datalst"""
        data_str = str(data_lst)[1:-1] + "\n"
        if all(v is np.nan for v in data_lst):
            continue
            """if no data in string don't write to file
               and print something saying no data
            """
        else:
            print(str(id_num) + " Vaisala" + " data: \n" + data_str)
            local_file.write(data_str)
            local_file.flush()
            remote_file.write(data_str)
            remote_file.flush()
            continue
            """if data lst has any data in it we write to the local
               and remote files and save them
            """


def main():
    """open daemons based on number of vaisala's found"""
    global infile
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
    """above processes infile and handles missing lines"""
    loc_nat, loc_sue = (infile[0], infile[1])
    if (loc_nat != "" and loc_sue != ""):
        print("Both Vaisalas connected")
        """define first raeading thread"""

        def vais1():
            ser1 = serial.Serial(loc_nat, baudrate=19200, timeout=1)
            id_num = "Natasha"
            file1 = create_log_file(id_num)
            interprate_vaisala_string(ser1, file1, id_num)
        t1 = threading.Thread(target=vais1)
        """define second raeading thread"""

        def vais2():
            ser2 = serial.Serial(loc_sue, baudrate=19200, timeout=1)
            id_num = "Susannah"
            file2 = create_log_file(id_num)
            interprate_vaisala_string(ser2, file2, id_num)
        t2 = threading.Thread(target=vais2)
        t1.setDaemon(True)
        t2.setDaemon(True)
        t1.start()
        t2.start()
    elif (loc_nat != "" and loc_sue == ""):
        print("Susannah Vaisala not connected log for only Natasha only")

        def vais1():
            ser1 = serial.Serial(loc_nat, baudrate=19200, timeout=1)
            id_num = "Natasha"
            file1 = create_log_file(id_num)
            interprate_vaisala_string(ser1, file1, id_num)
        t1 = threading.Thread(target=vais1)
        t1.setDaemon(True)
        t1.start()
    elif (loc_nat == "" and loc_sue != ""):
        print("Natasha Vaisala not connected log for only Susannah only")

        def vais1():
            ser1 = serial.Serial(loc_sue, baudrate=19200, timeout=1)
            id_num = "Susannah"
            file1 = create_log_file(id_num)
            interprate_vaisala_string(ser1, file1, id_num)
        t1 = threading.Thread(target=vais1)
        t1.setDaemon(True)
        t1.start()
    else:
        print("No Vaisalas are connected")
        return

if __name__ == "__main__":
    main()
