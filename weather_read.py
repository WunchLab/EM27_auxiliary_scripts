# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from mcculw import ul
from mcculw.enums import ULRange
from mcculw.ul import ULError
from mcculw.enums import  AnalogInputMode 
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
import datetime as dt
import pytz
import time
import threading
from time import sleep
import os

utc = pytz.timezone("utc")

id_num="ptb110_clarity"

#Pressure carlibration values    
V=np.array([0.2502, 1.000, 1.999, 2.5002, 3.7497, 4.9497])
P= np.array([910.0, 940.0, 980.0, 1000.0, 1050.0, 1098.0])

V=V.reshape(-1,1) 
P=P.reshape(-1,1) 

regr = linear_model.LinearRegression()
# Train the model using the training sets
lr=regr.fit(V, P)
cf=lr.coef_[0,0]
inter=lr.intercept_[0]


####reading from PTB110#####
board_num = 0
channel = 0
ai_range = ULRange.UNI5VOLTS
input_mode = AnalogInputMode.DIFFERENTIAL
value = ul.a_in(board_num, channel, input_mode)


####reading from Clarity####
import win32com.client as win32
clar=win32.gencache.EnsureDispatch('ClarityII.CloudSensorII')


def create_log_file(id_num=""):
    global local_file, header, base_name
    out_dir = 'C:/Users/Administrator/Desktop/em-27_aux_scripts/weather/' #output directory for files J
    base_name = (out_dir + dt.date.today().strftime("%Y%m%d") + "_" + str(id_num)) #full base filename J
    header = ("UTCDate,UTCTime,Pout, P_raw_voltage,WSPD,Tout,RH, Rain, Cloud, Daylight" +"\n")
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

  
    
leave_loop= False

while not leave_loop:

    try:
      create_log_file(id_num)
      # Get a value from the device
      value = ul.a_in(board_num, channel, input_mode)
      # Convert the raw value to engineering units
      V = ul.to_eng_units(board_num, input_mode, value)
      P = V*cf+inter


      measurement_datetime= dt.datetime.now(utc)
      measurement_time = measurement_datetime.strftime("%H:%M:%S.%f")
      measurement_date = measurement_datetime.strftime("%Y/%m/%d")
      Cloud=clar.CloudCondition
      Tout=clar.AmbientT
      WSPD=clar.Wind
      Rain=clar.RainCondition
      RH=clar.HumidityPercent
      Light=clar.DayCondition
      pprint=np.round(P , 2)
      vprint=np.round(V , 4)
      print(measurement_date+ "," +measurement_time+ ","+  str(pprint) + ","+ str(vprint)+ ","+ str(WSPD)+","+str(Tout)+","+str(RH)+","+str(Rain)+","+str(Cloud)+","+str(Light)+"\n")
      string=measurement_date+ "," +measurement_time+ ","+  str(pprint)+","+ str(V)+ ","+ str(WSPD)+","+str(Tout)+","+str(RH)+","+str(Rain)+","+str(Cloud)+","+str(Light)
      #UTCDate=np.append(UTCDate, measurement_date)     
      #UTCTime=np.append(UTCTime, measurement_time)     
      #Pout=np.append(Pout, P)     
      #f=open(local_file, 'a')
      #out_line = unicode(string) 
      local_file.write(string+ "\n")
      #f.flush()
      local_file.close()
      sleep(1)           
    except ULError as e:
      # Display the error
      print("A UL error occurred. Code: " + str(e.errorcode)
            + " Message: " + e.message)
  
