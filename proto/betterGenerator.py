from random import randint,choice,randrange
# I'm attempting to rebuild the levelgenerator to
# be more flexible and provide easier grid manipulation
# i'll be modeling it off this beautiful example by:
# Jay (Battery)                                                                                                              #
# https://whatjaysaid.wordpress.com/
# for how use it got to:
# https://whatjaysaid.wordpress.com/2016/01/15/1228
#
# though i'll be skipping over the frivolous explanations
#tile constants, i'll find a better way of storing these later
EMPTY = 0
FLOOR = 1
HALL = 2
DOOR = 3
DEADEND = 4
WALL = 5
OBSTACLE = 6
CAVE = 7
FRUIT = 8


class Room:
    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

class Generator:
    def __init__(self,width,height):
        self.width = abs(width)
        self.height = abs(height)
        self.grid = [[EMPTY for i in range(self.width)] for i in range(self.height)]
        self.rooms = []
        self.doors = []
        self.halls = []
        self.deadends = []
        self.graph = {}

    def __iter__(self): # allows the generator object to be iterated
        for x in range(self.width):
            for y in range(self.height):
                yield x, y, self.grid[x][y]

    def neighbors(self,x,y):
        # takes a cell:x,y arg
        #returns a generator with x,y indices of cell neighbors
        xi = (0,-1,1) if 0 < x < self.width-1 else ((0,-1) if x > 0 else (0,1))
        yi = (0,-1,1) if 0 < y < self.height-1 else ((0,-1) if y > 0 else (0,1))
        for a in xi:
            for b in yi:
                if a == b == 0:
                    continue
                yield (x+a,y+b)

    def directNeighbors(self,x,y):
        # cell: x,y arg
        # returns cell neighbors up,down,left,right
        xi = (0,-1,1) if 0 < x < self.width-1 else ((0,-1) if x > 0 else (0,1))
        yi = (0,-1,1) if 0 < y < self.height-1 else ((0,-1) if y > 0 else (0,1))
        for a in xi:
            for b in yi:
                if abs(a) == abs(b):
                    continue
                yield (x+a,y+b)

    def canCarve(self,x,y,xd,yd):
        #used by possibleMoves()
        # x,y int
        #xd,yd direction trying to move:
        #(-1,0)left (1,0)right (0,1)up (o,-1)down
        xi = (-1,0,1) if not xd else (1*xd,2*xd)
        yi = (-1,0,1) if not yd else (1*yd,2*yd)
        for a in xi:
            for b in yi:
                if self.grid[a+x][b+y]:
                    return False
        return True

    def possibleMoves(self,x,y):
        #searches for directions a hall can expand
        #used by generatePath()
        #returns a list of tuples of xy coords the path can move
        available = []
        for nx,ny in self.directNeighbors(x,y):
            if nx < 1 or ny < 1 or nx > self.width-2 or ny > self.height-2: continue
            xd = nx-x
            yd = ny-y
            if self.canCarve(x,y,xd,yd):
                available.append((nx,ny))
        return available

    def quadFits(self,sx,sy,rx,ry,margin):
        #sx,sy bottom left
        #rx,ry width height
        #margin int; space in grid cells
        sx -= margin
        sy -= margin
        rx += margin*2
        ry += margin*2
        if sx + rx < self.width and sy + ry < self.height and sx >= 0 and sy >= 0:
            for x in range(rx):
                for y in range(ry):
                    if self.grid[sx+x][sy+y]:
                        return False
            return True
        return False

    def floodFill(self,x,y,fillWith,tilesToFill = [],grid = None):
        #x,y where to start flood fill
        # with, tile constant to fill with
        # toFill, list of int; allows you to control what gets filled, all if left out
        # grid list[[]] 2d array to flood fill
        #returns none
        if not grid: grid = self.grid
        toFill = set()
        toFill.add((x,y))
        count = 0
        while toFill:
            x,y = toFill.pop()
            if tilesToFill and grid[x][y] not in tilesToFill: continue
            if not grid[x][y]: continue
            grid[x][y] = fillWith
            for nx,ny in self.directNeighbors(x,y):
                if grid[nx][ny] != fillWith:
                    toFill.add((nx,ny))
            count += 1
            if count > self.width*self.height:
                print('overrun')
                break

    def findEmptySpace(self,dist):
        for x in range(dist,self.width-dist):
            for y in range(dist,self.width-dist):
                touching = 0
                for xi in range(-dist,dist):
                    for yi in range(-dist,dist):
                        if self.grid[x+xi][y+yi]:touching += 1
                if not touching:
                    return x,y
        return None,None

    def findUnconnectedAreas(self):
        unconnected = []
        areaCount = 0
        gridCopy = [[EMPTY for i in range(self.width)] for i in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y]:
                    gridCopy[x][y] = 'x'
        for x in range(self.width):
            for y in range(self.height):
                if gridCopy[x][y] == 'x':
                    unconnected.append([])
                    areaCount += 1
                    self.floodFill(x,y,areaCount,None,gridCopy)
        for x in range(self.width):
            for y in range(self.height):
                if gridCopy[x][y]:
                    i = gridCopy[x][y]
                    unconnected[i-1].append((x,y))
        return unconnected

    def findDeadends(self):
        #populates self.deadends and is used by pruneDeadends()
        self.deadends = []
        for x, y in self.halls:
            touching = 0
            for nx,ny in self.directNeighbors(x,y):
                if self.grid[nx][ny]: touching += 1
            if touching == 1: self.deadends.append((x,y))

    def placeRoom(self,rx,ry,w,h,overlap = False):
        # place a quad within grid and add to self.rooms
        if self.quadFits(rx,ry,w,h,0) or overlap:
            for x in range(w):
                for y in range(h):
                    self.grid[rx+x][ry+y] = FLOOR
            self.rooms.append(Room(rx,ry,w,h))
            return True

    def placeRandomRooms(self,minrs,maxrs,roomGrow=1,margin=1,attempts=500):
        for a in range(attempts):
            rw = randrange(minrs,maxrs,roomGrow)
            rh = randrange(minrs,maxrs,roomGrow)
            rx = randint(0,self.width)
            ry = randint(0,self.height)
            if self.quadFits(rx,ry,rw,rh,margin):
                for x in range(rw):
                    for y in range(rh):
                        self.grid[rx+x][ry+y] = FLOOR
                self.rooms.append(Room(rx,ry,rw,rh))

#lets stack dicking with things shall we?
    def cellularAutomata(self,p=45,smoothing=4,using=EMPTY):
        #this is the cellular automata algorithm to generate
        # patterns other than 'cave'
        #using is the tile to be used,empty or 0 by default
        for x in range(self.width):
            for y in range(self.height):
                if randint(1,100)<p:
                    self.grid[x][y] = using
        for i in range(smoothing):
            for x in range(self.width):
                for y in range(self.height):
                    if x == 0 or x == self.width or y == 0 or y == self.height:
                        self.grid[x][y] = EMPTY
                    touchesEmpty = 0
                    for nx,ny in self.neighbors(x,y):
                        if self.grid[nx][ny] == using:
                            touchesEmpty += 1
                    if touchesEmpty >= 5:
                        self.grid[x][y] = using
                    elif touchesEmpty <= 2:
                        self.grid[x][y] = EMPTY

    def generateCaves(self,p=45,smoothing = 4):
        # using cellular automata
        #p:probability a tile turns CAVE
        # smoothing value, lower is more jagged
        for x in range(self.width):
            for y in range(self.height):
                if randint(0,100)<p:
                    self.grid[x][y] = CAVE
        for i in range(smoothing):
            for x in range(self.width):
                for y in range(self.height):
                    if x == 0 or x == self.width or y == 0 or y == self.height:
                        self.grid[x][y] = EMPTY
                    touchesEmpty = 0
                    for nx,ny in self.neighbors(x,y):
                        if self.grid[nx][ny] == CAVE:
                            touchesEmpty += 1
                    if touchesEmpty >= 5:
                        self.grid[x][y] = CAVE
                    elif touchesEmpty <= 2:
                        self.grid[x][y] = EMPTY

    def generateHalls(self,mode = 'r', x= None,y = None):
        #mode: 'r' random,
        #'f' first cell
        #'m' similar to first but snakey
        # 'l' snaking winding halls
        #x,y int of grid to start generating
        cells = []
        if not x and not y:
            x = randint(1,self.width-2)
            y = randint(1,self.height-2)
            while not self.canCarve(x,y,0,0):
                x = randint(1,self.width-2)
                y = randint(1,self.height-2)
        self.grid[x][y] = HALL
        self.halls.append((x,y))
        cells.append((x,y))
        while cells:
            if mode == 'l':
                x,y = cells[-1]
            elif mode == 'r':
                x,y = choice(cells)
            elif mode == 'f':
                x,y = cells[0]
            elif mode == 'm':
                x,y = cells[len(cells)//2]
            pm = self.possibleMoves(x,y)
            if pm:
                xi,yi = choice(pm)
                self.grid[xi][yi] = HALL
                self.halls.append((xi,yi))
                cells.append((xi,yi))
            else:
                cells.remove((x,y))

    def pruneDeadends(self,amount):
        for i in range(amount):
            self.findDeadends()
            for x,y in self.deadends:
                self.grid[x][y] = EMPTY
                self.halls.remove((x,y))
        self.findDeadends()

    def placeWalls(self):
        for x in range(self.width):
            for y in range(self.height):
                if not self.grid[x][y]:
                    for nx,ny in self.neighbors(x,y):
                        if self.grid[nx][ny] and self.grid[nx][ny] is not WALL:
                            self.grid[x][y] = WALL
                            break

    def connectRooms(self,extraDoorChance = 0):
        #attempts to connect rooms, but returns a list of
        # island areas; unconnected
        unconnected = []
        for r in self.rooms:
            connections = []
            for i in range(r.width):
                if self.grid[r.x+i][r.y-2]:
                    connections.append((r.x+i,r.y-1))
                if r.y+r.height+1 < self.height and self.grid[r.x+i][r.y+r.height+1]:
                    connections.append((r.x+i,r.y+r.height))
            for i in range(r.height):
                if self.grid[r.x-2][r.y+i]:
                    connections.append((r.x-1,r.y+i))
                if r.x +r.width+1 < self.width and self.grid[r.x+r.width+1][r.y+i]:
                    connections.append((r.x+r.width,r.y+i))
            if connections:
                chance = -1
                while chance <= extraDoorChance:
                    pickAgain = True
                    while pickAgain:
                        x,y = choice(connections)
                        pickAgain = False
                        for xi,yi in self.neighbors(x,y):
                            if self.grid[xi][yi] == DOOR:
                                pickAgain = True
                                break
                    chance = randint(0,100)
                    self.grid[x][y] = DOOR
                    self.doors.append((x,y))
            else:
                unconnected.append(r)
        return unconnected

    def joinUnconnected(self,unconnected):
        connections = []
        while len(unconnected) >= 2:
            bestDist = self.width + self.height
            c = [None,None]
            toConnect = unconnected.pop()
            for a in unconnected:
                for x,y in a:
                    for xi,yi in toConnect:
                        dist = abs(x-xi) + abs(y-yi)
                        if dist < bestDist and (x == xi or y == yi):
                            bestDist = dist
                            c[0] = (x,y)
                            c[1] = (xi,yi)
            c.sort()
            x,y = c[0]
            for x in range(c[0][0]+1,c[1][0]):
                if self.grid[x][y] == EMPTY:
                    self.grid[x][y] = HALL
            for y in range(c[0][1]+1,c[1][1]):
                if self.grid[x][y] == EMPTY:
                    self.grid[x][y] = HALL
            self.halls.append((x,y))


# path finding functions
    def constructNavGraph(self):
        for x,y in self.halls:
            if self.grid[x][y] < WALL: break
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y] not in [WALL,EMPTY,OBSTACLE]:
                    self.graph[(x,y)] = []
                    for nx,ny in self.directNeighbors(x,y):
                        if self.grid[nx][ny] not in [WALL,EMPTY,OBSTACLE]:
                            self.graph[(x,y)].append((nx,ny))

    def findPath(self,sx,sy,ex,ey):
        # args startx, starty, endx, endy
        # returns list of grid cells (x,y) leading from end to start
        # like [(ex,ey) ... (sx,sy)] to support popping of the end as agent moves
        cells = []
        cameFrom = {}
        cells.append((sx,sy))
        cameFrom[(s,sy)] = None
        while cells:
            #manhattan distance sort but it's slow;
            #cells.sort(key=lambda x: abs(ex-x[0]) + abs(ey-x[1]))
            current = cells[0]
            del cells[0]
            if current == (ex,ey):
                break
            for nx,ny in self.graph[current]:
                if (nx,ny) not in cameFrom:
                    cells.append((nx,ny))
                    cameFrom[(nx,ny)] = current
        if (ex,ey) in cameFrom:
            path = []
            current = (ex,ey)
            path.append(current)
            while current != (sx,sy):
                current = cameFrom[current]
                path.append(current)
            return path
