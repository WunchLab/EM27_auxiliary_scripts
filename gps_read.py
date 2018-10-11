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
from serial.tools import list_ports


#TODO use gpgrms for date
now = dt.datetime.now().strftime("%Y%m%d")

out_dir = 'C:/Users/Administrator/Desktop/em-27_aux_scripts/76_gps/' #output directory for files J
base_name = out_dir + now + "_" + "GPS_tb_" #initial filename + directory J
file_number = 0
for file in os.listdir(out_dir):
    if file == now + "_" + "GPS_tb_" + str(file_number).zfill(2)+".txt":
        file_number = file_number + 1
file_number = str(file_number).zfill(2)

header = "GPSUTCDate, GPSUTCTime, Lat, Long, masl, CompDate, CompTime\n"
log_file = open(base_name + file_number+".txt", mode="w") #open file for writing J

log_file.write(header)
"""remove these if not working """
try:
    gps_port = list(list_ports.grep("Prolific*"))
except StopIteration:
      print ("No device found")
loc_gps  = gps_port[0][0]
print("The GPS COM port is", loc_gps)

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
                time = str(int(float(time[0:2]))).zfill(2)+":"+str(int(float(time[2:4]))).zfill(2)+":"+str(int(float(time[4:6]))).zfill(2)
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
                         str(dt.datetime.now().strftime("%Y/%m/%d"))  + ", " + str(dt.datetime.now().strftime("%H:%M:%S")) + "\n"
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
