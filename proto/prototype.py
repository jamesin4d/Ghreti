import random, os.path
from pygame.locals import *
import pygame as pg
import sys
import random
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
screenRect = Rect(0,0,800,600)
fullscreen = False
windowFlags = 0 # 0 for none |FULLSCREEN

# Classes section
#-------------------------------------------------
class dummySound:
    def play(self): pass
#-----------------------------
class Entity(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
    def update(self):
        pass


#-----------------------------
class Timer:
    def __init__(self,length):
        self.count = 0
        self.length = length
        self.active = True
    def updating(self):
        if not self.active:
            return None
        if self.count < self.length:
            self.count += 1
        if self.count >= self.length:
            self.count = 0
            return True
        return False
    def setLength(self,value):
        self.length = value
    def deactivate(self):
        self.active = False
    def activate(self):
        self.count = 0
        self.active = True

#-------------------------------
class Engine:
    def __init__(self):
        self.current = State()
        self.states = []
    def run(self):
        self.states = [self.current]
        while self.states:
            self.current = self.states.pop()
            if self.current.paused:
                self.current.unpause()
            n, p = self.current.mainloop()
            if self.current.killPrev and self.states:
                self.states.pop()
            if p: #paused states are kept
                self.states.append(self.current)
            if n: #next state to go to
                self.states.append(n)
#-----------------------------------
class State:
    def __init__(self):
        self.done = False
        self.next = None
        self.paused = False
        self.killPrev = False
        self.clock = pg.time.Clock()
        self.screen = pg.display.get_surface()
        self.fullscreen = False

    def toggleFullscreen(self):
        if not self.fullscreen:
            print("going fullscreen")
            scr = pg.display.get_surface()
            scrbu = scr.copy()
            scr = pg.display.set_mode(screenRect.size,0|FULLSCREEN)
            scr.blit(scrbu,(0,0))
        else:
            scr = pg.display.get_surface()
            scrbu = scr.copy()
            scr = pg.display.set_mode(screenRect.size,0)
            scr.blit(scrbu,(0,0))
        pg.display.flip()
        self.fullscreen = not self.fullscreen
    def checkEvents(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.quit()
    def tick(self):
        self.clock.tick(60)
    def reinit(self):
        pass
    def togglePause(self):
        self.paused = not self.paused
        self.done = False
        self.next = None
    def mainStart(self):
        pass
    def update(self):
        pass
    def quit(self):
        self.done = True
        self.screen.fill((30,30,30))
        return self.next,self.paused
    def closeGame(self):
        sys.exit(0)
    def mainloop(self):
        self.mainStart()
        while not self.done:
            self.checkEvents()
            self.update()
            self.tick()
            pg.event.pump()
        return self.next,self.paused

class Camera:
    def __init__(self,w,h):
        self.cameraFunction = self.simple
        self.view = pg.Rect(0,0,w,h)

    def apply(self,target):
        return target.rect.move(self.view.topleft)
    def update(self,target):
        self.view = self.cameraFunction(self.view,target.rect)
    def simple(self,target):
        scr = pg.display.get_surface()
        hw = scr.width/2
        hh = scr.height/2
        l,t,_,_ = target
        _,_,w,h = self.view
        return pg.Rect(-l+hw,-t+hh,w,h)
    def complex(self,target):
        scr = pg.display.get_surface()
        r = scr.get_rect()
        ww = r.width
        wh = r.height
        hw = ww/2
        hh = wh/2
        l,t,_,_ = target
        _,_,w,h = self.view
        l,t,_,_ = -l+hw,-t+hh,w,h
        l = min(0,l) #halts scrolling at left edge
        l = max(-(self.view.width-ww),l) #right
        t = max(-(self.view.height-wh),t)#bottom
        t = min(0,t)    # and top
        return pg.Rect(l,t,w,h)


#helper functions
#---------------------------------------------
def loadSound(file):
    if not pg.mixer: return dummySound()
    file = os.path.join(mainDir,'snd',file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print('warning unable to load, %s' % file)
        return dummySound()

def loadImage(file):
    file = os.path.join(mainDir,'img',file)
    try:
        surf = pg.image.load(file)
    except pg.error:
        raise SystemExit('couldnt load image "%s" %s'%(file,pg.get_error()))
    return surf.convert()

def loadImages(*files):
    imgs = []
    for f in files:
        imgs.append(loadImage(f))
    return imgs

def pullFrames(file,sx,sy,ix,iy,convert=False):
    file = os.path.join(mainDir,'img',file)
    frames = []
    if convert:
        sh = pg.image.load(file).convert()
    else:
        sh = pg.image.load(file)
    sh.set_colorkey((255,255,255))
    for y in range(0,sy,iy):
        for x in range(0,sx,ix):
            r = Rect(x,y,ix,iy)
            t = sh.subsurface(r)
            frames.append(t)
    return frames


#-----------------------------------------------------
# level generator yo
class Generator:
    def __init__(self,w=64,h=64,mr=15,minrs=10,maxrs=15,ro=False,rc=1,rs=3,dts=16):
        self.levelRect = (w*dts,h*dts)
        self.width = w
        self.height = h
        self.tileSize = dts
        self.maxRooms =  mr
        self.minRoomSize = minrs
        self.maxRoomSize = maxrs
        self.roomsOverlap = ro
        self.randomConnections = rc
        self.randomSpurs = rs
        self.level = []
        self.rooms = []
        self.halls = []
        self.backgrounds = loadImages('Blue.png','Brown.png','Gray.png','Green.png')
        self.terrain = pullFrames("Terrain (16x16).png",352,176,16,16,True)
        self.characterTiles = {'blank': ' ','back':'.','wall':'#'}
        self.tiles = {
        'black' :self.terrain[23],
        'back' : self.backgrounds[0],
        'wall' : self.terrain[34]
        }
        self.characterLevel = []
    def generateRoom(self):
        w = random.randint(self.minRoomSize,self.maxRoomSize)
        h = random.randint(self.minRoomSize,self.maxRoomSize)
        x = random.randint(1,(self.width-w-1))
        y = random.randint(1,(self.height-h-1))
        return [x,y,w,h]
    def roomOverlapping(self,room,roomList):
        x = room[0]
        y = room[1]
        w = room[2]
        h = room[3]
        for r in roomList:
            if (x<(r[0]+r[2]) and
                r[0]<(x+w) and
                y<(r[1]+r[3]) and
                r[1]<(y+h)):
                return True
        return False
    def hallBetweenPoints(self,x,y,z,t,jt = 'either'):
        # x,y are one point z,t are another
        #jt:jointype is "either", "top","bottom"
        w = self.width
        h = self.height
        if x == z and y == t or x == z or y == t:
            return [(x,y),(z,t)]
        else:
            join = None
            if jt is 'either' and set([0,1]).intersection(set([x,y,z,t])):
                join = 'bottom'
            elif jt is 'either' and set([w-1,w-2]).intersection(set([x,z])) or set([h-1,h-2]).intersection(set([y,t])):
                join = 'top'
            elif jt is 'either':
                join = random.choice(['top','bottom'])
            else:
                join = jt
            if join is 'top':
                return [(x,y),(x,t),(z,t)]
            elif join is 'bottom':
                return [(x,y),(z,y),(z,t)]
    def joinRooms(self,r1,r2,jt='either'):
        #sort rooms by value of x
        sr = [r1,r2]
        sr.sort(key=lambda xy: xy[0])
        #first room
        x = sr[0][0]
        y = sr[0][1]
        w = sr[0][2]
        h = sr[0][3]
        x1 = x + w - 1
        y1 = y + h - 1
        #second room
        xx = sr[1][0]
        yy = sr[1][1]
        ww = sr[1][2]
        hh = sr[1][3]
        x2 = xx + ww - 1
        y2 = yy + hh - 1
        #overlapping on x
        if x < (xx+ww) and xx < (x+w):
            jx = random.randint(xx,x1)
            jxx = jx
            tmpy = [y,yy,y1,y2]
            tmpy.sort()
            jy = tmpy[1] + 1
            jyy = tmpy[2] - 1
            hall = self.hallBetweenPoints(jx,jy,jxx,jyy)
            self.halls.append(hall)
        #overlapping on y axis
        elif y < (yy+hh) and yy < (y+h):
            if yy > y:
                jy = random.randint(yy,y1)
                jyy = jy
            else:
                jy = random.randint(y,y2)
                jyy = jy
            tmpx = [x,xx,x1,x2]
            tmpx.sort()
            jx = tmpx[1] + 1
            jxx = tmpx[2] - 1
            hall = self.hallBetweenPoints(jx,jy,jxx,jyy)
            self.halls.append(hall)
        else:
            join = None
            if jt is 'either':
                join = random.choice(['top','bottom'])
            else:
                join = jt
            if join is 'top':
                if yy > y:
                    jx = x1 + 1
                    jy = random.randint(y,y1)
                    jxx = random.randint(xx,x2)
                    jyy = yy -1
                    h = self.hallBetweenPoints(jx,jy,jxx,jyy,'bottom')
                    self.halls.append(h)
                else:
                    jx = random.randint(x,x2)
                    jy = y - 1
                    jxx = xx - 1
                    jyy = random.randint(yy,y2)
                    h = self.hallBetweenPoints(jx,jy,jxx,jyy,'top')
                    self.halls.append(h)
            elif join is 'bottom':
                if yy > y:
                    jx = random.randint(x,x1)
                    jy = y1 + 1
                    jxx = xx -1
                    jyy = random.randint(yy,y2)
                    h = self.hallBetweenPoints(jx,jy,jxx,jyy,'top')
                    self.halls.append(h)
                else:
                    jx = x1 + 1
                    jy = random.randint(y,y1)
                    jxx = random.randint(xx,x2)
                    jyy = y2 + 1
                    h = self.hallBetweenPoints(jx,jy,jxx,jyy,'bottom')
                    self.halls.append(h)

    def generateLevel(self):
        # empty room and hall lists build empty level
        for i in range(self.height):
            self.level.append(['black']*self.width)
        self.rooms = []
        self.halls = []
        #make rooms
        for a in range(self.maxRooms*5):
            tr = self.generateRoom()
            if self.roomsOverlap or not self.rooms:
                self.rooms.append(tr)
            else:
                tr = self.generateRoom()
                tl = self.rooms[:]
                if self.roomOverlapping(tr,tl) is False:
                    self.rooms.append(tr)
            if len(self.rooms) >= self.maxRooms:
                break
        #connect rooms
        for a in range(len(self.rooms)-1):
            self.joinRooms(self.rooms[a],self.rooms[a+1])
        #make random connections
        for a in range(self.randomConnections):
            r1 = self.rooms[random.randint(0,len(self.rooms)-1)]
            r2 = self.rooms[random.randint(0,len(self.rooms)-1)]
            self.joinRooms(r1,r2)
        #random spurs
        for a in range(self.randomSpurs):
            r1 = [random.randint(2,self.width-2),random.randint(2,self.height-2),1,1]
            r2 = self.rooms[random.randint(0,len(self.rooms)-1)]
            self.joinRooms(r1,r2)
        #fill level, paint rooms
        for r,room in enumerate(self.rooms):
            for w in range(room[2]):
                for h in range(room[3]):
                    self.level[room[1]+h][room[0]+w]='back'
        #paint hhalls
        for hall in self.halls:
            x,y = hall[0]
            xx,yy = hall[1]
            for w in range(abs(x-xx)+3):
                for h in range(abs(y-yy)+3):
                    self.level[min(y,yy)+h][min(x,xx)+w] = 'back'
            if len(hall) == 3:
                x3,y3 = hall[2]
                for w in range(abs(xx-x3)+3):
                    for h in range(abs(yy-y3)+3):
                        self.level[min(yy,y3)+h][min(xx,x3)+w] = 'back'
        #paint walls
        for y in range(1,self.height-1):
            for x in range(1,self.width-1):
                if self.level[y][x] == 'back':
                    if self.level[y-1][x-1] == 'black':
                        self.level[y-1][x-1] = 'wall'
                    if self.level[y-1][x] == 'black':
                        self.level[y-1][x] = 'wall'
                    if self.level[y-1][x+1] == 'black':
                        self.level[y-1][x+1] = 'wall'
                    if self.level[y][x-1] == 'black':
                        self.level[y][x-1] = 'wall'
                    if self.level[y][x+1] == 'black':
                        self.level[y][x+1] = 'wall'
                    if self.level[y+1][x-1] == 'black':
                        self.level[y+1][x-1] = 'wall'
                    if self.level[y+1][x] == 'black':
                        self.level[y+1][x] = 'wall'
                    if self.level[y+1][x+1] == 'black':
                        self.level[y+1][x+1] = 'wall'

    def populatesprites(self):
        #right now this only populates the character tiles
        # for a printed map
        # todo while iterating through produce gameobjects
        # to a list to be given to the GameState
        spr = []
        for rn,r in enumerate(self.level):
            tmp = []
            for cn, c in enumerate(r):
                if c == 'black':
                    tmp.append(self.characterTiles['blank'])
                    ent = Entity()
                    ent.image = self.tiles['black']
                    ent.rect = ent.image.get_rect()
                    ent.rect.x = rn*ent.rect.width
                    ent.rect.y = cn*ent.rect.height
                    spr.append(ent)
                if c == 'back':
                    tmp.append(self.characterTiles['back'])
                    ent = Entity()
                    ent.image = self.tiles['back']
                    ent.rect = ent.image.get_rect()
                    ent.rect.x = (rn*ent.rect.width)/4
                    ent.rect.y = (cn*ent.rect.height)/4
                    spr.append(ent)
                if c == 'wall':
                    tmp.append(self.characterTiles['wall'])
                    ent = Entity()
                    ent.image = self.tiles['wall']
                    ent.rect = ent.image.get_rect()
                    ent.rect.x = rn*ent.rect.width
                    ent.rect.y = cn*ent.rect.height
                    ent.solid = True
                    spr.append(ent)
            self.characterLevel.append(''.join(tmp))
        #[print(r) for r in self.characterLevel]
        return spr

#--------------------------------
#PLAYER CLASS OBJECT SHTHING
#--------------------------------
class Player(Entity):
    def __init__(self):
        Entity.__init__(self)
        self.idleFrames = pullFrames('Idle (32x32).png',352,32,32,32,True)
        self.currentFrame = self.idleFrames[0]
        self.rect = self.currentFrame.get_rect()
#----------------------------------------------
# states are going here, I know its out of my order laid out earlier
class GameState(State):
    def __init__(self):
        State.__init__(self)
    def mainStart(self):
        self.player = Player()
        self.generator = Generator()
        self.camera = Camera(self.generator.levelRect[0],self.generator.levelRect[1])
        self.generator.generateLevel()
        self.spriteList = self.generator.populatesprites()

    def update(self):
        #check events
        for s in self.spriteList:
            self.screen.blit(s.image,self.camera.apply(s))
        pg.display.flip()
        #handle movement
        #when the player moves :camera.update(player)
        #do collision checks
        # update screen images like:
        # for i in images: screen.blit(i.image,camera.apply(i))
        pass


    def checkEvents(self):
        for e in pg.event.get():
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                self.closeGame()
            #elif e.type == KEYDOWN:
            #    if e.key == pg.K_f:
            #        self.toggleFullscreen()
            # todo triggers pg.error please call SDL_GetWindowSurface


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
