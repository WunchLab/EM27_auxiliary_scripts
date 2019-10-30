# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 13:48:21 2019

@author: Administrator
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


#create the file####

id_num="ptb110"
out_dir = 'C:/Users/Administrator/Desktop/em-27_auxiliary_scripts/weather/' #output directory for files J
file_name = (out_dir + dt.date.today().strftime("%Y%m%d") + "_" + str(id_num)+ ".txt")
header = ("UTCDate,UTCTime,WDIR,WSPD,Tout,RH,Pout,rainaccum,rainintensity,hailaccum,hailintensityd, ID" +"\n"
          )

f=open(file_name, 'a')

out_line = unicode("test", 'utf-8')

out_line = unicode(POUT)

f.write(out_line)

f.close()
close(file_name)

os.system("taskkill /im C:/Users/Administrator/Desktop/em-27_auxiliary_scripts/weather/20191030_ptb110.txt")


#Pressure= eng_units_value*cf+inter




board_num = 0
channel = 0
ai_range = ULRange.UNI5VOLTS
input_mode = AnalogInputMode.SINGLE_ENDED
value = ul.a_in(board_num, channel, input_mode)

leave_loop= False

POUT=[]

while not leave_loop:

    try:
      # Get a value from the device
      value = ul.a_in(board_num, channel, input_mode)
      # Convert the raw value to engineering units
      P = ul.to_eng_units(board_num, input_mode, value)*cf+inter

      measurement_datetime= dt.datetime.now(utc)
      measurement_time = measurement_datetime.strftime("%H:%M:%S.%f")
      measurement_date = measurement_datetime.strftime("%Y/%m/%d")
      # Display the raw value
      print("Raw Value: " + str(value))
      # Display the engineering value
      print("Pressure is: " + .join(map((P)))
      print("Time is:" +measurement_time)
      print("Date is:" +measurement_date)
      POUT=np.append(POUT, P)     
      sleep(1)           
    except ULError as e:
      # Display the error
      print("A UL error occurred. Code: " + str(e.errorcode)
            + " Message: " + e.message)
  
