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

pygame.init()
#pygame.mouse.set_visible(False)

size = width, height = 320, 240
screen = pygame.display.set_mode(size)

compass_background = pygame.image.load('compass_background.png')
compass_background = pygame.transform.scale(compass_background, (200,200))
compass_needle = pygame.image.load('compass_needle.png')
compass_needle = pygame.transform.scale(compass_needle, (190,190))
cb_rect = compass_background.get_rect()
cn_rect = compass_background.get_rect()

cb_rect.centerx = 160
cb_rect.centery = 120
cn_rect.centerx = 160
cn_rect.centery = 120

font = pygame.font.Font(None, 20)

quit_text = font.render("QUIT",1,(255,250,255))   #set up texts as buttons
q_text_pos = quit_text.get_rect()
q_text_pos.centerx = screen.get_rect().centerx + 100
q_text_pos.centery = screen.get_rect().centery + 100

compass_text = font.render("COMPASS",1,(255,250,255))
c_text_pos = compass_text.get_rect()
c_text_pos.centerx = 70
c_text_pos.centery = 220

display_compass = 0

while 1:
  temperature = getTMP()
  #Handle value error due to incorrect math domain
  try:
    heading = calcHeading()
  except ValueError:
    pass
  for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:
      p = pygame.mouse.get_pos()
      print p
      #touch screen button press detection logic, for quit button
      if p[0]>240 and p[0]<285 and p[1]>200 and p[1]<220: 
        sys.exit()
      elif p[0]>50 and p[0]<90 and p[1]>200 and p[1]<230:
        display_compass ^= 1

#  print "temperature is " + str(temperature)
#  print "heading is " + str(heading)

  screen.fill(black)
  screen.blit(quit_text, q_text_pos)
  screen.blit(compass_text, c_text_pos)
  if display_compass:
    screen.blit(compass_background, cb_rect)
    screen.blit(compass_needle, cn_rect)
  pygame.display.flip()
  time.sleep(0.05)
