import pygame as pg
from entity import *
import random
import os.path
mainDir =  os.path.split(os.path.abspath(__file__))[0]

class Fruit(Entity):
    def __init__(self,pos,*groups):
        super().__init__(pos,*groups)
        self.frameChoices = ["Apple.png","Bananas.png","Cherries.png","Kiwi.png","Melon.png"]
        framechoice = random.choice(self.frameChoices)
        self.frames = self.pullFrames(framechoice,544,32,32,32)
        self.collectedFrames = self.pullFrames("Collected.png",192,32,32,32)
        self.frameIndex = 0
        self.image = self.frames[self.frameIndex]
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.width = 16
        self.rect.height = 16
        self.collected = False

    def update(self):
        if not self.collected:
            self.frameIndex += 1
            if self.frameIndex == len(self.frames):
                self.frameIndex = 0
            self.image = self.frames[self.frameIndex]
        else:
            self.image = self.collectedFrames[5]
            self.kill()

    def pullFrames(self,file,sx,sy,ix,iy):
        file = os.path.join(mainDir,'img/Fruits',file)
        frames = []
        sh = pg.image.load(file).convert()
        #sh.convert_alpha()
        sh.set_colorkey((0,0,0))
        for y in range(0,sy,iy):
            for x in range(0,sx,ix):
                r = pg.Rect(x,y,ix,iy)
                t = sh.subsurface(r)
                frames.append(t)
        return frames
