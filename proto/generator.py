from util import *
import random
#-----------------------------------------------------
# level generator yo
class Generator:
    def __init__(self,h=50,w=38,mr=5,minrs=10,maxrs=18,ro=True,rc=1,rs=1,dts=16):
        self.levelRect = (w*dts,h*dts)
        #print(self.levelRect)
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
        #self.backgrounds = loadImages('Blue.png','Brown.png','Gray.png','Green.png')
        self.terrain = pullFrames("Terrain (16x16).png",352,176,16,16,True)
        self.characterTiles = {'blank': ' ','back':'.','wall':'#'}
        self.tiles = {
        'black' :self.terrain[23],
        'back' : self.terrain[33],
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
            r1 = [random.randint(2,self.width-2),random.randint(2,self.height-2),3,3]
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
            for w in range(abs(x-xx)+1):
                for h in range(abs(y-yy)+1):
                    self.level[min(y,yy)+h][min(x,xx)+w] = 'back'
                    #this seems to fix the list index out of range error
                    #by checking if that index exists,meant to widen halls
                    if self.level[min(y,yy)+h+1][min(x,xx)+w+1]:
                        self.level[min(y,yy)+h+1][min(x,xx)+w+1] = 'back'
            if len(hall) == 3:
                x3,y3 = hall[2]
                for w in range(abs(xx-x3)+1):
                    for h in range(abs(yy-y3)+1):
                        self.level[min(yy,y3)+h][min(xx,x3)+w] = 'back'
                        if self.level[min(yy,y3)+h+1][min(xx,x3)+w+1]:
                            self.level[min(yy,y3)+h+1][min(xx,x3)+w+1] = 'back'
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
        fg = []
        for rn,r in enumerate(self.level):
            tmp = []
            for cn, c in enumerate(r):
                if c == 'black':
                    tmp.append(self.characterTiles['blank'])
                    #ent = Entity()
                    #fr = Frames()
                    #fr.current = self.tiles['black']
                    #rect = fr.current.get_rect()
                    #rect.x = rn*rect.width
                    #rect.y = cn*rect.height
                    #ent.setMulti(fr,rect)
                    #spr.append(ent)
                if c == 'back':
                    tmp.append(self.characterTiles['back'])
                    #ent = Entity()
                    #fr = Frames()
                    #fr.current = self.tiles['back']
                    #rect = fr.current.get_rect()
                    #rect.x = rn*rect.width
                    #rect.y = cn*rect.height
                    #ent.setMulti(fr,rect)
                    #spr.append(ent)
                if c == 'wall':
                    tmp.append(self.characterTiles['wall'])
                    #ent = Entity()
                    #fr = Frames()
                    #fr.current = self.tiles['wall']
                    #rect = fr.current.get_rect()
                    #rect.x = rn*rect.width
                    #rect.y = cn*rect.height
                    #ent.setMulti(fr,rect)
                    #fg.append(ent)
            self.characterLevel.append(''.join(tmp))
        #[print(r) for r in self.characterLevel]
        return self.characterLevel
