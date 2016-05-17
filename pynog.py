import obd_io
import os
import threading
import sys
import serial
import platform
import time
import ConfigParser
from subprocess import call
from obd2_codes import pcodes
from obd2_codes import ptest
from obd_utils import scanSerial


ID_ABOUT = 101
ID_EXIT = 110
ID_CONFIG = 500
ID_CLEAR = 501
ID_GETC = 502
ID_RESET = 503
ID_LOOK = 504
ALL_ON = 505
ALL_OFF = 506

ID_DISCONNECT = 507
ID_HELP_ABOUT = 508
ID_HELP_VISIT = 509
ID_HELP_ORDER = 510


#call("sudo rfcomm connect 0 00:1D:A5:00:0F:A1",shell=True)
time.sleep(3)
port = obd_io.OBDPort( "/dev/rfcomm0"  ,2,5,0)

def initCommunication():
  #call("sudo rfcomm connect 0 00:1D:A5:00:0F:A1 &>/dev/null",shell=True)
  if port.State == 0:
    return None
  active = []

  supp = port.sensor(0)[1]
  print "Comm initialized"
  print active
  print supp
  for i in range(1, len(supp)):
    if supp[i-1] == "1": #put X in coloum if PID is supported
      active.append(1)
    else:
      active.append(0)
  #while(1):
    #for i in range(len(supp)):
  #  for i in range(50):
     # if supp[i]=="1":
  #      try:
  #        print `((port.sensor(12)[1]-1346500000)-689000)/10.55-700`+"RPM"
  #      except:
  #        print "ERROR ERROR"
initCommunication()


def getRPM():
  try:
   # return ((port.sensor(12)[1]-1346500000)-689000)/10.5-700
    rpms = port.sensor(12)[1]
    rpms = rpms & 0x0000FFFF
    return int(rpms) 
  except:
    return "err"

def getSpeed():
  try:
    speeds =  port.sensor(13)[1]
    speeds = int(speeds) 
    speeds = speeds & 0x000000FF
    speeds /= 1.609
    return int(speeds)
  except:
    return "Drugs are bad mmmkay?"

def getCoolantTemp():
  try:
    return port.sensor(5)[1] & 0x000000FF
  except:
    return "err"

def getIntakeTemp():
  try:
    return port.sensor(15)[1] & 0x00000000FF
  except:
    return "err"

def getThrottle():
  try:
    return int((port.sensor(17)[1] & 0x00000000FF)* 100.0 / 255.0)
  except:
    return "err"

def getLoad():
  try:
    return int(( port.sensor(4)[1] & 0x00000000FF)*100.0/255.0)
  except:
    return "err"
