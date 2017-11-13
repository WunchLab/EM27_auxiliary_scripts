# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 16:22:23 2017

@author: sajjan
"""

import serial
import datetime as dt
import os
import numpy as np
import pytz
import threading
import time
utc = pytz.timezone("utc")


#TODO use gpgrms for date
now = dt.datetime.now().strftime("%Y%m%d")

out_dir = 'C:/Users/Administrator/Desktop/em-27_aux_scripts/75_gps/' #output directory for files J
base_name = out_dir + now + "_" + "GPS_" #initial filename + directory J
file_number = 0
for file in os.listdir():
    if file == base_name + str(file_number).zfill(2):
        file_number = file_number + 1
file_number = str(file_number).zfill(2)

header = "GPSUTCDate, GPSUTCTime, Lat, Long, masl, CompTime\n"
log_file = open(base_name + file_number, mode="w") #open file for writing J

log_file.write(header)
"""remove these if not working """
gps_infile = open("./gps_infile", mode="r").readlines()
gps_infile = [x for x in gps_infile if x[0] != "#"]
loc_gps = gps_infile[0]


def gps_read():
    global stop_event, loc_gps
    gps_ser = serial.Serial(loc_gps, baudrate=4800, timeout=1)
#    data_dict = {"GPGGA": [], "GPRMC": [], "GPGSA": [], "GPGSV": []}
    while not stop_event.is_set():
        gps = str(gps_ser.readline())[2:-5].split(",")
        date = dt.datetime.now(utc).strftime("%Y/%m/%d")

#        data_dict[sentence[0]].append(sentence[1:])
        if gps[0] == "$GPGGA":
            lat = str(gps[2])
            time = (gps[1])
            try:
                lat = float(lat[0:2]) + float(lat[2:])/60.
                lon = str(gps[4])
                lon = -float(lon[0:3]) - float(lon[3:])/60.
                alt = float(gps[9])
            except KeyboardInterrupt:
                log_file.close()
                raise
            except ValueError:
                time, lat, lon, alt = (np.nan, np.nan, np.nan, np.nan)
            data_str = [time, lat, lon, alt]
            write_str = (date + ", " + str(data_str[0]) + ", " + str(data_str[1:])[1:-1] + ", " +
                         str(dt.datetime.now()) + "\n"
                         )
            print("GPS Fix Data: \n " + write_str)
            log_file.write(write_str)
            log_file.flush()
    log_file.close()
    gps_ser.close()


def gps_daemon():
    global stop_event
    stop_event = threading.Event()
    t1 = threading.Thread(target=gps_read)
    t1.setDaemon(True)
    t1.start()


def stop():
    stop_event.set()
    time.sleep(1)
    exit()
if __name__ == "__main__":
    gps_daemon()
