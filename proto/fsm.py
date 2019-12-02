import pygame as pg
import sys
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
        pass
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
