#Hud.py
#This program will compile all the IMU and OBDII readings
#and display them onto the TFT screen.
#Created by XiaoXing Zhao and William Voge
#Edited 5/16/2016

import pygame
import sys
import os
import time
from rpiIMU import *
from temp_read import *

os.environ['SDL_VIDEODRIVER'] = 'fbcon'   #set up os environment to display to TFT
os.environ['SDL_FBDEV'] = '/dev/fb1'
os.environ['SDL_MOUSEDEV'] = '/dev/input/touchscreen' #set up touchscreen as mouse input
os.environ['SDL_MOUSEDRV'] = 'TSLIB'

black = 0, 0, 0
white = 255, 255, 255
blue = 84,179,247
red = 255, 71, 71

pygame.init()
pygame.mouse.set_visible(False)

size = width, height = 320, 240
screen = pygame.display.set_mode(size)

compass_background = pygame.image.load('compass_background.png')
compass_background = pygame.transform.scale(compass_background, (200,200))
compass_needle = pygame.image.load('compass_needle.png')
compass_needle = pygame.transform.scale(compass_needle, (150,150))
cb_rect = compass_background.get_rect()
cn_rect = compass_background.get_rect()

cb_rect.centerx = 165
cb_rect.centery = 107
cn_rect.centerx = 193
cn_rect.centery = 130

font = pygame.font.Font(None, 20)
font2 = pygame.font.Font(None, 30)
font3 = pygame.font.Font(None, 27)

quit_text = font.render("QUIT",1,(255,250,255))   #set up texts as buttons
q_text_pos = quit_text.get_rect()
q_text_pos.centerx = screen.get_rect().centerx + 100
q_text_pos.centery = screen.get_rect().centery + 100

compass_text = font.render("COMPASS",1,(255,250,255))
c_text_pos = compass_text.get_rect()
c_text_pos.centerx = 70
c_text_pos.centery = 220

degree_text = font2.render("degrees",1,(255,250,255))
d_text_pos = degree_text.get_rect()
d_text_pos.centerx = 295
d_text_pos.centery = 25

temp_text = font2.render("temp",1,(255,250,255))
t_text_pos = temp_text.get_rect()
t_text_pos.centerx = 265
t_text_pos.centery = 176

accel_text = font3.render("accel",1,(255,250,255))
a_text_pos = accel_text.get_rect()
a_text_pos.centerx = 245
a_text_pos.centery = 105

velocity_text = font3.render("velocity",1,(255,250,255))
v_text_pos = velocity_text.get_rect()
v_text_pos.centerx = 60
v_text_pos.centery = 40

rpm_text = font3.render("rpm",1,(255,250,255))
r_text_pos = velocity_text.get_rect()
r_text_pos.centerx = 165
r_text_pos.centery = 40

dir_text = font3.render("N",1,(255,250,255))
dir_text_pos = velocity_text.get_rect()
dir_text_pos.centerx = 280
dir_text_pos.centery = 40

display_compass = 0     #toggle displaying compass
display_F = 0           #toggle displaying fahrenheit
display_kph = 0         #toggle displaying km per hour

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

time_count = 0
acceleration = 0

while 1:
  time_count += 1
  temperature = getTMP()
  #velocity = getVelocity()
  #rpm = getRMP()
  #Handle value error due to incorrect math domain
  try:
    heading = int(calcHeading()) - 20
    if heading < 0:
      heading = 360 + heading
    if time_count % 2: 
      acceleration = calcAcceleration()
  except ValueError:
    pass

  for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:
      p = pygame.mouse.get_pos()
      #touch screen button press detection logic, for quit button
      if p[0]>240 and p[0]<285 and p[1]>200 and p[1]<220: 
        sys.exit()
      elif p[0]>50 and p[0]<90 and p[1]>200 and p[1]<230:
        display_compass ^= 1
      elif p[0]>213 and p[0]<300 and p[1]>140 and p[1]<200 :
        display_F ^= 1
      elif p[0]>20 and p[0]<width/3 and p[1]>20 and p[1]<70:
        display_kph ^= 1 

  print "temperature is " + str(temperature)
  print "heading is " + str(heading)
  print "acceleration is " + str(acceleration)

  screen.fill(black)
  screen.blit(quit_text, q_text_pos)
  screen.blit(compass_text, c_text_pos)

  if display_compass:
    degree_text = font2.render(str(int(heading))+'\xb0', 1,(84,179,247))
    screen.blit(degree_text, d_text_pos)
    screen.blit(compass_background, cb_rect)
    new_compass_needle = rot_center(compass_needle, heading)  #added 90 as offset
    screen.blit(new_compass_needle, cn_rect)
  else:
    pygame.draw.line(screen, white, (20, 70), (300, 70))  
    pygame.draw.line(screen, white, (20, 140), (300, 140))  
    pygame.draw.line(screen, white, (width/3, 20), (width/3, 200))  
    pygame.draw.line(screen, white, (2*width/3, 20), (2*width/3, 200))  

    if display_F:
      temperature = int(temperature * 9.0/5.0 + 32)
      temp_text = font2.render(str(int(temperature))+'\xb0F', 1, blue)  
    else:
      temp_text = font2.render(str(int(temperature))+'\xb0C', 1, blue)   
    screen.blit(temp_text, t_text_pos) 

    if acceleration < 1:
      accel_text = font3.render('~0 m/s\xb2', 1, blue)
    else:
      accel_text = font3.render('%.2f m/s\xb2'%acceleration, 1, blue)
    screen.blit(accel_text, a_text_pos)

    if display_kph:
      velocity_text = font3.render('96 km/h', 1, blue)
    else:
      velocity_text = font3.render('69 mph', 1, blue)
    screen.blit(velocity_text, v_text_pos)
    
    if heading < 22.5 or heading > 337.5:
      dir_text = font2.render("N", 1, red)     
    elif heading > 22.5 and heading < 67.5:
      dir_text = font2.render("NE", 1, red)
    elif heading > 67.5 and heading < 112.5:
      dir_text = font2.render("E", 1, red)
    elif heading > 112.5 and heading < 157.5:
      dir_text = font2.render("SE", 1, red)
    elif heading > 157.5 and heading < 202.5:
      dir_text = font2.render("S", 1, red)
    elif heading > 202.5 and heading < 247.5:
      dir_text = font2.render("SW", 1, red)
    elif heading > 247.5 and heading < 292.5:
      dir_text = font2.render("W", 1, red)
    else:
      dir_text = font2.render("NW", 1, red)
    screen.blit(dir_text, dir_text_pos)

    rpm_text = font3.render('69 rpm', 1, blue)
    screen.blit(rpm_text, r_text_pos)

  pygame.display.flip()
  time.sleep(0.1)
