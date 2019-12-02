import pygame as pg#
--------------------------
#ENTITY
#-----------------------------
class Entity(pg.sprite.Sprite):
    def __init__(self, *components):
        pg.sprite.Sprite.__init__(self)
        self.components = {}
        for c in components:
            self.setComp(c)
    def setComp(self,c):
        k = type(c)
        self.components[k] = c
    def setMulti(self,*comps):
        for c in comps:
            self.setComp(c)
    def getMulti(self,*comps):
        for c in comps:
            yield self.getComp(c)
    def getComp(self,c):
        return self.components[c]
    def hasComp(self,c):
        if not c in self.components: return False
        else:
            return self.components[c] is not None
    def update(self):
        pass

#-----------------------------
#COMPONENTS
#-----------------------------
class Vel:
    def __init__(self):
        self.x = 0
        self.y = 0
class Frames:
    current = None
    def __init__(self):
        pass
class Grav:
    def __init__(self,v=3):
        self.val = v
class Input:
    def __init__(self):
        self.left = False
        self.right = False
        self.jump = False

#------------------------------
#SYSTEM
#------------------------------
class System:
    attached = None#world it's attached to
    priority = 0 # order the system is ran
    def attach(self,to):
        if self.attached is not None:
            raise Exception('system already attached')
        else:
            self.attached = to
    def process(self):
        raise NotImplementedError
#----------------
#WORLD
#----------------
class World:
    def __init__(self):
        self.systems = []
        self.entities = {}
    def addEnt(self,e):
        if not e in self.entities:
            self.entities[e] = e
    def removeEnt(self,e):
        if self.entities[e] is not None:
            self.entities.remove(e)
    def clearEnts(self):
        self.entities.clear()
    def addSys(self,sys,p=0):
        if not sys in self.systems:
            sys.priority = p
            sys.attach(self)
            self.systems.append(sys)
            self.systems.sort(key=lambda s: s.priority,reverse=True)
    def removeSys(self,sys):
        self.systems[sys].attached = None
        self.systems.remove(sys)
    def runSys(self):
        for s in self.systems:
            s.process()
