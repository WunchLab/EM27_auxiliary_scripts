

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
out_dir = 'C:/Users/Administrator/Desktop/em-27_aux_scripts/weather/' #output directory for files J
file_name = (out_dir + dt.date.today().strftime("%Y%m%d") + "_" + str(id_num)+ ".txt")
header = ("UTCDate,UTCTime,Pout, P_raw_voltage,WSPD,Tout,RH, Rain, Cloud")
f=open(file_name, 'a')
out_line = unicode(header) 
f.write(out_line+ "\n")
f.close()


#carlibration values    
V=np.array([0.2502, 1.000, 1.999, 2.5002, 3.7497, 4.9497])
P= np.array([910.0, 940.0, 980.0, 1000.0, 1050.0, 1098.0])

plt.plot(V, P)

V=V.reshape(-1,1) 
P=P.reshape(-1,1) 

regr = linear_model.LinearRegression()
# Train the model using the training sets
lr=regr.fit(V, P)
cf=lr.coef_
inter=lr.intercept_



####reading from PTB110#####

board_num = 0
channel = 0
ai_range = ULRange.UNI5VOLTS
input_mode = AnalogInputMode.DIFFERENTIAL
value = ul.a_in(board_num, channel, input_mode)

leave_loop= False

####reading from Clarity####
import win32com.client as win32
clar=win32.gencache.EnsureDispatch('ClarityII.CloudSensorII')


while not leave_loop:

    try:
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
      pprint=round(P,2)
      vprint=round(V,4)
      print(measurement_date+ "," +measurement_time+ ","+  str(pprint) + ","+ str(vprint)+ ","+ str(WSPD)+","+str(Tout)+","+str(RH)+","+str(Rain)+","+str(Cloud)+"\n")
      string=measurement_date+ "," +measurement_time+ ","+  str(P)[1:-1][1:-1]+","+ str(V)+ ","+ str(WSPD)+","+str(Tout)+","+str(RH)+","+str(Rain)+","+str(Cloud)
      #UTCDate=np.append(UTCDate, measurement_date)     
      #UTCTime=np.append(UTCTime, measurement_time)     
      #Pout=np.append(Pout, P)     
      f=open(file_name, 'a')
      out_line = unicode(string) 
      f.write(out_line+ "\n")
      #f.flush()
      f.close()
      sleep(1)           
    except ULError as e:
      # Display the error
      print("A UL error occurred. Code: " + str(e.errorcode)
            + " Message: " + e.message)
  

