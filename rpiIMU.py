#!/usr/bin/python
#
#    Edited by XiaoXing Zhao on May 16, 2016
#
import smbus
import time
import math
from LSM9DS0 import *
import datetime

bus = smbus.SMBus(1)

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40      # Complementary filter constant
ACC_SENSITIVITY = 0.732/1000 #according to data sheet for linear acceleration +/- 16g range

def writeACC(register,value):
  bus.write_byte_data(ACC_ADDRESS , register, value)
  return -1

def writeMAG(register,value):
  bus.write_byte_data(MAG_ADDRESS, register, value)
  return -1

def writeGRY(register,value):
  bus.write_byte_data(GYR_ADDRESS, register, value)
  return -1

def readACCx():
  acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_X_L_A)
  acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_X_H_A)
  acc_combined = (acc_l | acc_h <<8)
  return acc_combined  if acc_combined < 32768 else acc_combined - 65536

def readACCy():
  acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Y_L_A)
  acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Y_H_A)
  acc_combined = (acc_l | acc_h <<8)
  return acc_combined  if acc_combined < 32768 else acc_combined - 65536

def readACCz():
  acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Z_L_A)
  acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Z_H_A)
  acc_combined = (acc_l | acc_h <<8)
  return acc_combined  if acc_combined < 32768 else acc_combined - 65536

def readMAGx():
  mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_X_L_M)
  mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_X_H_M)
  mag_combined = (mag_l | mag_h <<8)
  return mag_combined  if mag_combined < 32768 else mag_combined - 65536

def readMAGy():
  mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_Y_L_M)
  mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_Y_H_M)
  mag_combined = (mag_l | mag_h <<8)
  return mag_combined  if mag_combined < 32768 else mag_combined - 65536

def readMAGz():
  mag_l = bus.read_byte_data(MAG_ADDRESS, OUT_Z_L_M)
  mag_h = bus.read_byte_data(MAG_ADDRESS, OUT_Z_H_M)
  mag_combined = (mag_l | mag_h <<8)
  return mag_combined  if mag_combined < 32768 else mag_combined - 65536

def readGYRx():
  gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_X_L_G)
  gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_X_H_G)
  gyr_combined = (gyr_l | gyr_h <<8)
  return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536
  
def readGYRy():
  gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_Y_L_G)
  gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_Y_H_G)
  gyr_combined = (gyr_l | gyr_h <<8)
  return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536

def readGYRz():
  gyr_l = bus.read_byte_data(GYR_ADDRESS, OUT_Z_L_G)
  gyr_h = bus.read_byte_data(GYR_ADDRESS, OUT_Z_H_G)
  gyr_combined = (gyr_l | gyr_h <<8)
  return gyr_combined  if gyr_combined < 32768 else gyr_combined - 65536
	
#initialise the accelerometer
writeACC(CTRL_REG1_XM, 0b01100111) #z,y,x axis enabled, continuos update,  100Hz data rate
writeACC(CTRL_REG2_XM, 0b00100000) #+/- 16G full scale

#initialise the magnetometer
writeMAG(CTRL_REG5_XM, 0b11110000) #Temp enable, M data rate = 50Hz
writeMAG(CTRL_REG6_XM, 0b01100000) #+/-12gauss
writeMAG(CTRL_REG7_XM, 0b00000000) #Continuous-conversion mode

#initialise the gyroscope
writeGRY(CTRL_REG1_G, 0b00001111) #Normal power mode, all axes enabled
writeGRY(CTRL_REG4_G, 0b00110000) #Continuos update, 2000 dps full scale

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0
kalmanX = 0.0
kalmanY = 0.0

#Function used calculate the magnetometer heading in order to be used with the compass
def calcHeading():
  MAGx = readMAGx()
  MAGy = readMAGy()
  MAGz = readMAGz()
  ACCx = readACCx()
  ACCy = readACCy()
  ACCz = readACCz()
  
  #Normalize accelerometer raw values.
  ###################Calculate pitch and roll#########################
  #Us these two lines when the IMU is up the right way. Skull logo is facing down
  accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
  accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
  pitch = math.asin(accXnorm)
  roll = -math.asin(accYnorm/math.cos(pitch))

  #Calculate the new tilt compensated values
  magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
  magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)

  #Calculate tilt compensated heading
  tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI

  if tiltCompensatedHeading < 0:
    tiltCompensatedHeading += 360
  return tiltCompensatedHeading

#Function used to calculate the acceleration value
def calcAcceleration():
  #Read the accelerometer,gyroscope values
  ACCx = readACCx() * ACC_SENSITIVITY      #multiply raw reading by sensitvity to obtain acc in g's
  ACCy = readACCy() * ACC_SENSITIVITY
  ACCz = readACCz() * ACC_SENSITIVITY

  #Normalize x and y vectors to compensate for gravity
  thetaX = math.atan(ACCx/math.sqrt(ACCy**2+ACCz**2))
  thetaY = math.atan(ACCy/math.sqrt(ACCx**2+ACCz**2))
  
  ACCxComp = ACCx * math.cos(thetaX)
  ACCyComp = ACCy * math.cos(thetaY)

  acceleration = math.sqrt(ACCxComp**2 + ACCyComp**2) * 9.807
  return acceleration


