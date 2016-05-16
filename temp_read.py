#!/usr/bin/python

import smbus
import time
import math
import numpy
import datetime
from kalman_filter import *
from LSM9DS0 import *

bus = smbus.SMBus(1);         # 0 for R-Pi Rev. 1, 1 for Rev. 2
std_dev = 0.48
process_variance = 1e-5
estimated_measurement_variance = std_dev ** 2  # 0.05 ** 2
kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)

def writeTMP(register, value):
  bus.write_byte_data(TMP_ADDRESS, register, value)
  return -1

def readTMP():
  tmp_l = bus.read_byte_data(TMP_ADDRESS,  OUT_TEMP_L_XM)
  tmp_h = bus.read_byte_data(TMP_ADDRESS,  OUT_TEMP_H_XM)
  print tmp_l
  print tmp_h
  tmp_combined = ((tmp_h & 0b00001111) << 8) | tmp_l
  tmp_combined = tmp_combined if tmp_combined < 2048 else tmp_combined - 4096
  return tmp_combined     # add 16 as calibration factor

#initialize temperature sensor
def initTMP():
  writeTMP(CTRL_REG5_XM, 0b11110000)  #TMP enable, M data rate = 50Hz

#Calibrate temperature sensor using latest sensor data, mainly acquire std_dev value
def calibTMP():
  tmp_calibration = []
  while len(tmp_calibration) < 500:
    tmp_value = readTMP()
    tmp_calibration.append(tmp_value)
  print len(set(tmp_calibration))
  std_dev = numpy.std(tmp_calibration)
  print "Standard deviation of sensor is", std_dev
  estimated_measurement_variance = std_dev ** 2  # 0.05 ** 2
  kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)
  for iteration in xrange(1, len(tmp_calibration)):
    kalman_filter.input_latest_noisy_measurement(tmp_calibration[iteration])

#Obtain kalman-filtered temperature in Celsius, rounded to integer form
def getTMP():
  tmp_readings = []
  while len(tmp_readings) < 100:
    tmp_readings.append(readTMP())
  iteration_count = len(tmp_readings)
  for iteration in xrange(1, iteration_count):
    kalman_filter.input_latest_noisy_measurement(tmp_readings[iteration])
  temperature = kalman_filter.get_latest_estimated_measurement()
  print int(round(temperature))
  return temperature 

