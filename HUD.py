#Hud.py
#This program will compile all the IMU and OBDII readings
#and display them onto the TFT screen.
#Created by XiaoXing Zhao and William Voge
#Edited 5/16/2016

import pygame
import sys
import os
from rpiIMU import *
from rpiIMU import *

os.environ['SDL_VIDEODRIVER'] = 'fbcon'   #set up os environment to display to TFT
os.environ['SDL_FBDEV'] = '/dev/fb1'
os.environ['SDL_MOUSEDEV'] = '/dev/input/touchscreen' #set up touchscreen as mouse input
os.environ['SDL_MOUSEDRV'] = 'TSLIB'

black = 0, 0, 0

pygame.init()
pygame.mouse.set_visible(False)

size = width, height = 320, 240
screen = pygame.display.set_mode(size)

compass_background = pygame.image.load('compass_background.png')
compass_needle = pygame.image.load('compass_needle.png')
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

while 1:
  for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:
      p = pygame.mouse.get_pos()
      #touch screen button press detection logic, for quit button
      if not start and p[0]>240 and p[0]<285 and p[1]>200 and p[1]<220: 
        sys.exit()
  print "temperature is " `
  screen.fill(black)
  screen.blit(quit_text, q_text_pos)
  screen.blit(compass_background, cb_rect)
  screen.blit(compass_needle, cn_rect)
  pygame.display.flip()
