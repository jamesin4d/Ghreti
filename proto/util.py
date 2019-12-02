import pygame as pg
import os.path
import os
# Classes section
#-------------------------------------------------
class dummySound:
    def play(self): pass

mainDir =  os.path.split(os.path.abspath(__file__))[0]

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

def pullFrames(file,sx,sy,ix,iy,convert=True):
    file = os.path.join(mainDir,'img',file)
    frames = []
    if convert:
        sh = pg.image.load(file).convert()
    else:
        sh = pg.image.load(file)
    sh.set_colorkey((0,0,0))
    for y in range(0,sy,iy):
        for x in range(0,sx,ix):
            r = pg.Rect(x,y,ix,iy)
            t = sh.subsurface(r)
            frames.append(t)
    return frames
