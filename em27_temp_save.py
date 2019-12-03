# -*- coding: utf-8 -*-
"""
Created on Tue Feb 05 13:41:21 2019

@author: Nasrin Pak

This is to read the temperature from the sensor inside the EM27 and save
it into a text file.
"""

import os
#print os.getcwd()

import urllib2
import time


starttime=time.time()
while True:

#reading temperature and time and date times only
  response = urllib2.urlopen('http://10.10.0.1/diag_scan.htm')
  for line_number, line in enumerate(response):
      # Because this is 0-index based
      if line_number == 53:
          print line
          Temp=line
      if line_number == 54:
          print line
          Time=line
      # Stop reading
      elif line_number > 54:
          break

  with open('C:/Users/Administrator/Desktop/em-27_aux_scripts/75_temp/temp_dec.txt', 'a') as f:
      f.write(Time+ '\n')
      f.write(Temp+ '\n')
    
  time.sleep(30.0 - ((time.time() - starttime) % 30.0))  