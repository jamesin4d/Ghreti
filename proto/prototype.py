import random, os.path
from pygame.locals import *
import pygame as pg
from camera import *
#from generator import *
from betterGenerator import *
#from dungen import *
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
        #sh.convert_alpha()
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
        self.gravity = pg.Vector2((0,0.5))
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
        self.terrain = pullFrames("Terrain (16x16).png",352,176,16,16,True)
        self.characterTiles = {'blank': ' ','back':'.','wall':'#'}
        self.tiles = {
        'black' :self.terrain[23],
        'back' : self.terrain[33],
        'wall' : self.terrain[34]
        }
        self.generator = Generator(64,64)
        self.entities = CameraLayeredUpdate(self.player,pg.Rect(0,0,self.generator.width*16,self.generator.height*16))
        self.populateLevel()
    def populateLevel(self):
        level = [
            "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
            "P                                                  P",
            "P                             FFFFFFFF             P",
            "P                                                  P",
            "P                                                  P",
            "P       FFFFFFFFFFFFF                              P",
            "P                                                  P",
            "P                                   PPP            P",
            "P                                                  P",
            "P     PPPPPP                                       P",
            "P                              PPP                 P",
            "P                                                  P",
            "P                                                  P",
            "P                                                  P",
            "P                                                  P",
            "P                      PPPPP                       P",
            "P                                                  P",
            "P                                                  P",
            "P                                PP                P",
            "P           PPP   PP        FF                     P",
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
        self.generator.placeRandomRooms(4,10,2,4,3000)
        self.generator.generateHalls()
        self.generator.pruneDeadends(10)
        (hx,hy) = self.generator.halls[1]
        self.generator.placeWalls()
        self.generator.floodFill(hx,hy,HALL)

        self.generator.connectRooms(30)
        unconnected = self.generator.findUnconnectedAreas()
        #print(unconnected)
        self.generator.joinUnconnected(unconnected)
        #self.player.rect.x = self.player.rect.y = 50
        #self.generator.placeRoom(1,1,32,32,True)
        #self.generator.cellularAutomata(45,3,WALL)
        self.generator.placeWalls()
        print(self.generator.rooms)
        r = choice(self.generator.rooms)
        self.player.rect.x = r.x+r.width/2
        self.player.rect.y = r.y + r.height/2
        self.generator.floodFill(2,2,FRUIT,[HALL,FLOOR])

        self.entities.worldSize = pg.Rect(0,0,self.generator.width*16,self.generator.height*16)
        #print(self.generator.halls[0])
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
        for x,y,tile in self.generator:
            #print(tile)
            if tile == WALL:
                e = Entity((x*16,y*16),self.solids,self.entities)
                e.image = self.tiles['wall']
            if tile == HALL:
                print('hall')
                #e = Entity((x*16,y*16),self.entities)
                #e.image = self.tiles['black']
            if tile == FLOOR:
                print('floor')
            if tile == FRUIT:
                #print('fruit')
                e = Fruit((x*16,y*16),self.solids,self.entities)
    #    for rn,r in enumerate(self.generator.level):
    #        for cn, c in enumerate(r):
    #            if c == 'wall':
    #                e = Entity((x,y),self.solids,self.entities)
    #                e.image = tiles["wall"]
                #if c == 'L':
                #    self.player.rect.x = x
                #    self.player.rect.y = y
                #if c == 'F':
                #    f = Fruit((x,y),self.solids,self.entities)
    #            x+=self.generator.tileSize
    #        y+=self.generator.tileSize
    #        x = 0


    def update(self):
        # i want to say this is the order things should
        # be prioritized
        #check events
        #handle movement first on x axis then
        #check collisions,
        #then move on y axis,check collisions
        #when the player moves :camera.update(player)
        # update screen images
        #TODO player falls out of map, dies!
        self.entities.update()
        self.screen.fill((30,30,30))
        self.background.draw(self.canvas)
        self.entities.draw(self.canvas)
        tf = pygame.transform.scale(self.canvas,(400*2,300*2))
        self.screen.blit(tf,(0,0))
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
