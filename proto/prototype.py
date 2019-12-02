import random, os.path
from pygame.locals import *
import pygame as pg
from camera import *
from generator import *
from fsm import *
from timer import *
from input import *
from util import *
import sys
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (120,20)
#this fixed an error i was having with linux audio drivers
# i don't know why as the alsa driver is the one used by default
# and is the one throwing an overrun error. so without further ado
#TODO write an OS detection method to avoid this ruining your life
#
os.environ['SDL_AUDIODRIVER'] = 'alsa'

if not pg.image.get_extended():
    raise SystemExit("extended image module required")

# game constants
#-----------------------------------------------
mainDir =  os.path.split(os.path.abspath(__file__))[0]
screenRect = Rect((0,0,800,608))
fullscreen = False
windowFlags = 0 # 0 for none |FULLSCREEN

# Classes section
#-------------------------------------------------

# i'm doing away with the ecs model en lu of:
# sprites work as entities, attributes components
# and spritegroups call update and draw on everything
#what more do you need?
class Entity(pg.sprite.Sprite):
    def __init__(self,pos,*groups):
        super().__init__(*groups)
        self.image = pg.Surface((16,16))
        self.image.fill((255,180,180))
        self.rect = self.image.get_rect(topleft=pos)

class Frames:
    current = None
    def __init__(self):
        pass

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
        sh.set_colorkey((0,0,0))
        for y in range(0,sy,iy):
            for x in range(0,sx,ix):
                r = pg.Rect(x,y,ix,iy)
                t = sh.subsurface(r)
                frames.append(t)
        return frames
#--------------------------------
#PLAYER CLASS OBJECT SHTHING
#--------------------------------
class Player(Entity):
    def __init__(self,collides,inputhandler, pos,*groups):
        super().__init__(pos,*groups)
        self.collides = collides # a group of sprites to check collisions with
        self.frames = Frames()
        self.frames.idle = pullFrames('Idle (32x32).png',352,32,32,32,True)
        self.frames.current = self.frames.idle[0]
        self.image = self.frames.current
        self.rect = self.image.get_rect(topleft=pos)
        self.vel = pg.Vector2((0,0))
        self.speed = 8
        self.jump = 10
        self.gravity = pg.Vector2((0,0.5))
        self.sliding = pg.Vector2((0,0.1))
        self.onGround = False
        self.onWall = False
        self.input = inputhandler

    def update(self):
        self.input.handle()
        #

        if self.input.isPressed("up"):
            if self.onGround:
                self.vel.y = -self.jump
            if self.onWall:
                self.vel.y = -self.jump
                self.vel.x = self.speed *-1
                self.onWall = False
        if self.input.isHeld("left"):
            self.vel.x = -self.speed
        if self.input.isHeld("right"):
            self.vel.x = self.speed
        if not self.onGround:
            if self.onWall:
                self.vel.y += self.sliding.y
            else:
                self.vel.y += self.gravity.y

            if self.vel.y > 50: self.vel.y = 50
        if not(self.input.isHeld("left") or self.input.isHeld("right")):
            self.vel.x = 0
        self.rect.left += self.vel.x
        self.onWall = False
        self.collide(self.vel.x,0,self.collides)
        self.rect.top += self.vel.y
        self.onGround = False
        self.collide(0,self.vel.y,self.collides)

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


#----------------------------------------------
# states are going here, I know its out of my order laid out earlier
class GameState(State):
    def __init__(self):
        State.__init__(self)
    def mainStart(self):
        self.backgroundImages = loadImages('Blue.png','Brown.png','Gray.png','Green.png')
        self.inputhandler = Input()
        self.background = pg.sprite.Group()
        self.solids = pg.sprite.Group()
        self.canvas = pygame.Surface((400,300))
        self.scale = 2
        self.player = Player(self.solids,self.inputhandler,(3,12))
        self.generator = Generator()
        self.generator.generateLevel()
        self.entities = CameraLayeredUpdate(self.player,pg.Rect(0,0,self.generator.levelRect[0],self.generator.levelRect[1]))
        self.populateLevel()
    def populateLevel(self):
        level = [
            "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
            "P                                                  P",
            "P             F                            F       P",
            "P                                                  P",
            "P                    PPPPPPPPPPP                   P",
            "P          FFF                                     P",
            "P                                           F      P",
            "P                                   F              P",
            "P    PPPPPPPP                       F      PPPPPPPPP",
            "P                                                  P",
            "P                          PPPPPPP                 P",
            "P      FFF    FF  PPPPPP                           P",
            "P                                                  P",
            "P         PPPPPPP                                  P",
            "P                                                  P",
            "P     FFF             PPPPPP                       P",
            "P        FFFF                      F               P",
            "P   PPPPPPPPPPP                                    P",
            "P                                        FFF       P",
            "P                 PPPPPPPPPPP                  F   P",
            "P                                          PPPPPPPPP",
            "P                                         P    F PPP",
            "P                  L                            PPPP",
            "P                                             PPPPPP",
            "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]

        x = y = 0

        tiles = self.generator.tiles
        rooms = self.generator.rooms
        rr = random.choice(rooms)
        ts = self.generator.tileSize
        lw = len(level[0])*ts
        lh = len(level)*ts
        self.entities.worldSize = pg.Rect(0,0,lw,lh)
        cx = (rr[0]+(rr[2]/2))*ts
        cy = (rr[1]+(rr[3]/2))*ts
        self.player.rect.x = cx
        self.player.rect.y = cy
        #populate background tiles
        bgi = random.choice(self.backgroundImages)
        for rn,r in enumerate(level):
            for cn, c in enumerate(r):
                e = Entity((x,y),self.background)
                e.image = bgi
                x+= 32 #width of bg image
            y += 32
            x = 0 #height, maybe shouldn't hardcode
        x = y = 0
        for rn,r in enumerate(level):
            for cn, c in enumerate(r):
                if c == 'P':
                    e = Entity((x,y),self.solids,self.entities)
                    e.image = tiles["wall"]
                if c == 'L':
                    self.player.rect.x = x
                    self.player.rect.y = y
                if c == 'F':
                    f = Fruit((x,y),self.solids,self.entities)
                x+=self.generator.tileSize
            y+=self.generator.tileSize
            x = 0
    def update(self):
        # i want to say this is the order things should
        # be prioritized
        #check events
        #handle movement first on x axis then
        #check collisions,
        #then move on y axis,check collisions
        #when the player moves :camera.update(player)
        # update screen images
        self.entities.update()
        self.screen.fill((30,30,30))
        self.background.draw(self.screen)
        self.entities.draw(self.screen)
        #tf = pygame.transform.scale(self.canvas,(self.canvas.get_width()*self.scale,self.canvas.get_height()*self.scale))
        #self.screen.blit(self.canvas,(350,250))
        pg.display.update()


    def checkEvents(self):
        pass

#-------------
#begin code that runs

def mainStart():
    if pg.get_sdl_version()[0] == 2:
        print("hell yeah sdl 2")
        pg.mixer.pre_init(44100,32,2,1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("warning no sound")
        pg.mixer = None

    screen = pg.display.set_mode(screenRect.size,windowFlags)
    pg.display.set_caption("Ghreti: Prototyping")
    icon = loadImage("Fall (32x32).png")
    pg.display.set_icon(icon)
    engine = Engine()
    engine.current = GameState()
    engine.run()

mainStart()
