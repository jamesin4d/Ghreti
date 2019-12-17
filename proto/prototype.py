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
from entity import *
from fruit import *
from player import *
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
def gatherResources():
    backgroundImages = loadImages('Blue.png','Brown.png','Gray.png','Green.png')
    terrain = pullFrames("Terrain (16x16).png",352,176,16,16,True)
    characterTiles = {'blank': ' ','back':'.','wall':'#'}
    tiles = {
    'black' :terrain[23],
    'back' : terrain[33],
    'wall' : terrain[34]
    }
# i'm doing away with the ecs model en lu of:
# sprites work as entities, attributes components
# and spritegroups call update and draw on everything
#what more do you need?
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
        self.generator.floodFill(2,2,FRUIT,[HALL])

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
                pass
                #print('hall')
                #e = Entity((x*16,y*16),self.entities)
                #e.image = self.tiles['black']
            if tile == FLOOR:
                print('floor')
            if tile == FRUIT:
                #print('fruit')
                e = Fruit((x*16,y*16),self.solids,self.entities)


    def update(self):

        #TODO player falls out of map, dies!
        self.entities.update()
        self.screen.fill((30,30,30))
        self.background.draw(self.canvas)
        self.entities.draw(self.canvas)
        tf = pygame.transform.scale(self.canvas,(400*2,300*2))
        self.screen.blit(tf,(0,0))
        pg.display.update()


class Tutorial(State):
    def __init__(self):
        self.nextState = GameState
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
#TODO move tiles and background images to be loaded at the very beginning
        self.tiles = {
        'black' :self.terrain[23],
        'back' : self.terrain[33],
        'wall' : self.terrain[34]
        }
        self.entities = CameraLayeredUpdate(self.player,pg.Rect(0,0,32*16,32*16))
        self.makeLevel()

    def makeLevel(self):
        level = [
            "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
            "P      FFFFFFF FF  FF FFFFF FFFFF FFFFFF FFFFFF    P",
            "P      FF      FF  FF FF  F FF      FF     FF      P",
            "P      FF  FFF FFFFFF FF    FFFF    FF     FF      P",
            "P      FF   FF FF  FF FF    FF      FF     FF      P",
            "P  PP  FFFFFFF FF  FF FF    FFFFF   FF   FFFFFF    P",
            "P                       PP                         P",
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
            "P                     PP   PPPPPPP P               P",
            "P      FFF    FF  PPPPPP           P               P",
            "P                     PP           P               P",
            "P         PPPPPPP     PPP FF       P               P",
            "P                     PP           P               P",
            "P     FFF             PPPPPP    F  P               P",
            "P        FFFF         PP           PP              P",
            "P   PPPPPPPPPPP       PP     F     P               P",
            "P                     PP           P     FFF       P",
            "P                 PPPPPPPPPPP   F  P           F   P",
            "P                     PP           P       PPPPPPPPP",
            "P                     PP     F F   P      P    F PPP",
            "P                  L  PP           P            PPPP",
            "P                     PP  FFFF     P          PPPPPP",
            "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]
        self.entities.worldSize = pg.Rect(0,0,len(level[0])*16,len(level)*16)
        x = y = 0
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
            for cn,c in enumerate(r):
                if c == "P":
                    e = Entity((x,y),self.solids,self.entities)
                    e.image = self.tiles["wall"]
                if c == "F":
                    e = Fruit((x,y),self.solids,self.entities)
                if c == "L":
                    self.player.rect.x = x
                    self.player.rect.y = y
                x += 16
            y += 16
            x = 0
        x=y=0
        print(len(level),len(level[0]))

    def printTutorial(self):
        pass

    def update(self):
        self.entities.update()
        self.screen.fill((30,30,30))
        self.background.draw(self.canvas)
        self.entities.draw(self.canvas)

        tf = pygame.transform.scale(self.canvas,(400*2,300*2))
        self.screen.blit(tf,(0,0))
        pg.display.update()

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
    engine.current = Tutorial()
    engine.run()

mainStart()
