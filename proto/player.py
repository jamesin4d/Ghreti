from entity import *
import pygame as pg
from util import *
from fruit import Fruit
class Frames:
    current = None
    def __init__(self):
        pass
#--------------------------------
#PLAYER CLASS OBJECT SHTHING
#--------------------------------
class Player(Entity):
    def __init__(self,collides,inputhandler, pos,*groups):
        super().__init__(pos,*groups)
        self.collides = collides # a group of sprites to check collisions with
        self.frames = Frames()
        self.frames.idle = pullFrames('Idle (32x32).png',352,32,32,32)
        self.frames.fall = pullFrames('Fall (32x32).png',32,32,32,32)
        self.frames.jump = pullFrames('Jump (32x32).png',32,32,32,32)
        self.frames.run = pullFrames('Run (32x32).png',384,32,32,32)
        self.frames.runLeft = pullFrames('Run (32x32).png',384,32,32,True,True)
        self.frames.current = self.frames.idle[0]
        self.frameIndex = 0
        self.image = self.frames.current
        self.rect = self.image.get_rect(topleft=pos)
        self.vel = pg.Vector2((0,0))
        self.speed = 4
        self.jump = 10
        self.gravity = pg.Vector2((0,0.4))
        self.sliding = pg.Vector2((0,0.01))
        self.onGround = False
        self.onWall = False
        self.input = inputhandler
        self.jumping = False
        self.falling = False
        self.idle = True
        self.right = False
        self.left = False

    def animate(self):

        if self.idle:
            self.frameIndex +=1
            if self.frameIndex == len(self.frames.idle): self.frameIndex = 0
            self.image = self.frames.idle[self.frameIndex]
        elif self.jumping:
            self.image = self.frames.jump[0]
        elif self.falling:
            self.image = self.frames.jump[0]
        elif self.right:
            frame = (self.rect.x//10) % len(self.frames.run)
            self.image = self.frames.run[frame]
        elif self.left:
            frame = (self.rect.x//10) % len(self.frames.run)
            self.image = pg.transform.flip(self.frames.run[frame],True,False)

    def update(self):
        self.input.handle()
        self.left = self.right = self.jumping = self.falling = self.idle = False
        if self.onWall and self.input.isPressed('up'):
            self.vel.y = -self.jump
        if self.input.isPressed("up"):
            if self.onGround:
                self.vel.y = -self.jump
                self.jumping = True
                self.falling = False
        if self.input.isHeld("left"):
            self.left = True
            self.right = False
            self.vel.x = -self.speed
        if self.input.isHeld("right"):
            self.right = True
            self.left = False
            self.vel.x = self.speed
        if not self.onGround:
            self.falling = True
            self.idle = self.jumping = False
            self.vel.y += self.gravity.y
            if self.onWall: self.vel.y += self.sliding.y
            if self.vel.y > 10: self.vel.y = 10
        if not(self.input.isHeld("left") or self.input.isHeld("right")):
            self.vel.x = 0
            self.right = self.left = False
            if self.falling or self.jumping:
                self.idle = False
            else: self.idle = True
        self.rect.left += self.vel.x
        self.onWall = False
        self.collide(self.vel.x,0,self.collides)
        self.rect.top += self.vel.y
        self.onGround = False
        self.collide(0,self.vel.y,self.collides)
        self.animate()
    def collide(self,xvel,yvel,others):
        for o in others:
            if pg.sprite.collide_rect(self,o):
                if isinstance(o,Fruit):
                    o.collected = True
                else:
                    if xvel > 0:
                        self.rect.right = o.rect.left
                        self.onWall = True
                        self.xvel = 0
                    if xvel < 0:
                        self.rect.left = o.rect.right
                        self.onWall = True
                        self.xvel = 0
                    if yvel < 0:
                        self.rect.top = o.rect.bottom
                    if yvel > 0:
                        self.rect.bottom = o.rect.top
                        self.onGround = True
                        self.yvel = 0
