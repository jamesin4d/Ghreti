#--------------------------------------------------------------------
from src.gameStateBase import *
from src.stateMachine import *
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (120,20)
os.environ['SDL_AUDIODRIVER'] = 'alsa'
def mainSetup():
    WIN_WIDTH = 800
    WIN_HEIGHT = 480
    DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
    #DEPTH = 32
    #FLAGS = 0
    #CAMERA_SLACK = 32
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("You're Making A Game!")
    pygame.key.set_repeat(1,1)
    e = Engine()
    e.currentState = GameState()
    e.run()
