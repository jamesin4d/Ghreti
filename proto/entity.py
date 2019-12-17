import pygame as pg
class Entity(pg.sprite.Sprite):
    def __init__(self,pos,*groups):
        super().__init__(*groups)
        self.image = pg.Surface((16,16))
        self.image.fill((255,180,180))
        self.rect = self.image.get_rect(topleft=pos)
