

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


id_num="clarity"
out_dir = 'C:/Users/Administrator/Desktop/em-27_aux_scripts/weather/' #output directory for files J
file_name = (out_dir + dt.date.today().strftime("%Y%m%d") + "_" + str(id_num)+ ".txt")
header = ("UTCDate,UTCTime,WSPD,Tout,RH, Rain, Cloud")
f=open(file_name, 'a')
out_line = unicode(header) 
f.write(out_line+ "\n")
f.close()


leave_loop= False

####reading from Clarity####
import win32com.client as win32
clar=win32.gencache.EnsureDispatch('ClarityII.CloudSensorII')


while not leave_loop:

    try:


      measurement_datetime= dt.datetime.now(utc)
      measurement_time = measurement_datetime.strftime("%H:%M:%S.%f")
      measurement_date = measurement_datetime.strftime("%Y/%m/%d")
      Cloud=clar.CloudCondition
      Tout=clar.AmbientT
      WSPD=clar.Wind
      Rain=clar.RainCondition
      RH=clar.HumidityPercent
      print(measurement_date+ "," +measurement_time+ ","+  str(WSPD)+","+str(Tout)+","+str(RH)+","+str(Rain)+","+str(Cloud)+"\n")
      string=measurement_date+ "," +measurement_time+ ","+  str(WSPD)+","+str(Tout)+","+str(RH)+","+str(Rain)+","+str(Cloud)
      f=open(file_name, 'a')
      out_line = unicode(string) 
      f.write(out_line+ "\n")
      f.close()
      sleep(1)           
    except ULError as e:
      # Display the error
      print("A UL error occurred. Code: " + str(e.errorcode)
            + " Message: " + e.message)
  

