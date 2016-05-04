#!/usr/bin/python

import smbus
import time
import math
import numpy
import datetime
from kalman_filter import *
from LSM9DS0 import *

bus = smbus.SMBus(1);         # 0 for R-Pi Rev. 1, 1 for Rev. 2
std_dev = 1.23
process_variance = 1e-5
estimated_measurement_variance = std_dev ** 2  # 0.05 ** 2
kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)

def writeTMP(register, value):
  bus.write_byte_data(TMP_ADDRESS, register, value)
  return -1

def readTMP():
  tmp_l = bus.read_byte_data(TMP_ADDRESS,  OUT_TEMP_L_XM)
  tmp_h = bus.read_byte_data(TMP_ADDRESS,  OUT_TEMP_H_XM)
  tmp_combined = (tmp_l | tmp_h << 8)
  tmp_combined = tmp_combined if tmp_combined < 32768 else tmp_combined - 65536
  return tmp_combined

def calibTMP():
  tmp_calibration = []
  writeTMP(CTRL_REG5_XM, 0b11110000)  #TMP enable, M data rate = 50Hz
  while len(tmp_calibration) < 500:
    tmp_calibration.append(readTMP())
  std_dev = numpy.std(tmp_calibration)
  print "Standard deviation of sensor is", std_dev
  estimated_measurement_variance = std_dev ** 2  # 0.05 ** 2
  kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)

#initialize temperature sensor
def initTMP():
  writeTMP(CTRL_REG5_XM, 0b11110000)  #TMP enable, M data rate = 50Hz

def getTMP():
  tmp_readings = []
  while len(tmp_readings) < 200:
    tmp_readings.append(readTMP())
  iteration_count = len(tmp_readings)
  for iteration in xrange(1, iteration_count):
    kalman_filter.input_latest_noisy_measurement(tmp_readings[iteration])
  temperature = kalman_filter.get_latest_estimated_measurement()
  print int(round(temperature))
  return kalman_filter.get_latest_estimated_measurement()
