import pygame as pg
import os
class Input:
    def __init__(self):
        pg.joystick.init()
        self.bound = {}
        self.pressed = {}
        self.held = {"key": [], "joy": [],"dpad": []}
        self.bind("left", pg.K_a)
        self.bind("left",pg.K_LEFT)
        self.bind("right",pg.K_d)
        self.bind("right",pg.K_RIGHT)
        self.bind("up",pg.K_w)
        self.bind("up",pg.K_UP)
        self.joystick = None
        for i in range(pg.joystick.get_count()):
            self.joystick = pg.joystick.Joystick(i)
            self.joystick.init()

    def handle(self):
        #print("inputhandler")
        self.events = pg.event.get()
        self.pressed = {"key":[],"joy":[],"dpad":[]}
        for e in self.events:
            #print(e)
            if e.type == pg.QUIT:
                pg.quit()
                quit()
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                self.pressed["key"].append(e.key)
                self.held["key"].append(e.key)
            if e.type == pg.KEYUP:
                if e.key in self.held["key"]:
                    self.held["key"].remove(e.key)
            if e.type == pg.JOYBUTTONDOWN:
                self.pressed["joy"].append(e.button)
                self.held["joy"].append(e.button)
            if e.type == pg.JOYBUTTONUP:
                if e.button in self.held["joy"]:
                    self.held["joy"].remove(e.button)
            if e.type == pg.JOYHATMOTION:
                vals = []
                if e.value[0]<0:
                    vals.append("dleft")
                if e.value[0]>0:
                    vals.append("dright")
                if e.values[1]>0:
                    vals.append("dup")
                if e.values[1]<0:
                    vals.append("ddown")
                for b in ["dleft","dright","dup","ddown"]:
                    if b in self.held["dpad"]:
                        self.held["dpad"].remove(b)
                    else:
                        for v in vals:
                            self.pressed["dpad"].append(v)
                            self.held["dpad"].append(v)
        #print(self.held)
    def bind(self,value,key):
        if not value in self.bound:
            self.bound[value] = []
        self.bound[value].append(key)

    def isPressed(self,value):
        if value in self.bound:
            bound = self.bound[value]
        for key in self.pressed:
            for i in self.pressed[key]:
                if i in bound:
                    return True
        return False

    def isHeld(self,value):
        if value in self.bound:
            bound = self.bound[value]
        for key in self.held:
            for i in self.held[key]:
                if i in bound:
                    return True
        return False


def test():
    pg.init()
    pg.display.set_mode((320,240))
    input = Input()
    while 1:
        #pg.time.wait(15)
        input.handle()

        if input.isPressed("up"):
            print("up is pressed")

        if input.isPressed("left"):
            print("left is pressed")

        if input.isPressed("right"):
            print("right is pressed")


if __name__ == "__main__":
    test()
