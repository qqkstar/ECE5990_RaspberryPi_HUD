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

display_compass = 0     #toggle displaying compass
display_F = 0           #toggle displaying fahrenheit

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

while 1:
  temperature = getTMP()
  #Handle value error due to incorrect math domain
  try:
    heading = int(calcHeading())
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

  print "temperature is " + str(temperature)
  print "heading is " + str(heading)

  screen.fill(black)
  screen.blit(quit_text, q_text_pos)
  screen.blit(compass_text, c_text_pos)
  if display_compass:
    degree_text = font2.render(str(int(heading))+'\xb0', 1,(84,179,247))
    screen.blit(degree_text, d_text_pos)
    screen.blit(compass_background, cb_rect)
    new_compass_needle = rot_center(compass_needle, heading+90)  #added 90 as offset
    screen.blit(new_compass_needle, cn_rect)
  else:
    pygame.draw.line(screen, white, (20, 70), (300, 70))  
    pygame.draw.line(screen, white, (20, 140), (300, 140))  
    pygame.draw.line(screen, white, (width/3, 20), (width/3, 200))  
    pygame.draw.line(screen, white, (2*width/3, 20), (2*width/3, 200))  
    if display_F:
      temperature = int(temperature * 9.0/5.0 + 32)
      temp_text = font2.render(str(int(temperature))+'\xb0F', 1, white)  
      screen.blit(temp_text, t_text_pos)
    else:
      temp_text = font2.render(str(int(temperature))+'\xb0C', 1, white)   
      screen.blit(temp_text, t_text_pos) 
  pygame.display.flip()
  time.sleep(0.1)
