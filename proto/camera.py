import pygame
from pygame import *

#canvas = pygame.surface
#blit everything to canvas
#apply camera transformations
# pygame.transform.scale(canvas,windowW,windowH)
#blit canvas to screen
#pygame.display.update
class Camera:
    def __init__(self,w,h):
        self.cameraFunction = self.complex
        self.view = pygame.Rect(0,0,w,h)

    def apply(self,target):
        return target.move(self.view.topleft)
    def update(self,target):
        self.view = self.cameraFunction(target)
    def simple(self,target):
        scr = pygame.display.get_surface()
        hw = scr.get_width()/2
        hh = scr.get_height()/2
        l,t,_,_ = target
        _,_,w,h = self.view
        return pygame.Rect(-l+hw,-t+hh,w,h)
    def complex(self,target):
        scr = pygame.display.get_surface()
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
        return pygame.Rect(l,t,w,h)
# subclassing sprite.LayeredUpdates
class CameraLayeredUpdate(pygame.sprite.LayeredUpdates):
    def __init__(self,target,worldSize):
        super().__init__() #init parent class
        self.target = target
        self.cam = pygame.Vector2(0,0) #using vector2
        self.worldSize = worldSize #size of world space
        self.screen = pygame.display.get_surface()
        self.canvas = pygame.Surface((400,300))
        self.scale = 2
        if self.target:
            self.add(target)
            self.move_to_front(self.target)

    def update(self, *args):
        super().update(*args)
        if self.target:
            r = self.target.rect
            sw = self.screen.get_width()
            sh = self.screen.get_height()
            x = -r.center[0]+sw/2
            y = - r.center[1]+sh/2
            self.cam += (pygame.Vector2((x,y))-self.cam)*0.05
            self.cam.x = max(-(self.worldSize.width-sw), min(0,self.cam.x))
            self.cam.y = max(-(self.worldSize.height-sh), min(0,self.cam.y))

    def draw(self,surface):
        sd = self.spritedict
        dirty = self.lostsprites
        self.lostsprites = []
        for spr in self.sprites():
            rec = sd[spr]
            newrect = surface.blit(spr.image,spr.rect.move(self.cam))
            if rec is self._init_rect:
                dirty.append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty.append(newrect.union(rec))
                else:
                    dirty.append(newrect)
                    dirty.append(rec)
                sd[spr] = newrect
        #tf = pygame.transform.scale(self.canvas,(self.canvas.get_width()*self.scale,self.canvas.get_height()*self.scale))
        #surface.blit(tf,(0,0))
        return dirty
