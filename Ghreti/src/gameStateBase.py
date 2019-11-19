from src.stateMachine import *
import sys
import pygame
from src.entCompSys import *
from src.components.image import *
from src.components.position import *
from src.components.velocity import * 

#generic parent class for a gamestate with methods specific to such
class GameState(State):
    def __init__(self):
        State.__init__(self)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.get_surface()
        self.world = World()
        player = self.world.createEntity()
        self.world.addComponent(player,Position(x=10,y=10))
        self.world.addComponent(player,Image('blue.png'))
        self.world.addComponent(player,Velocity())


    def update(self):
        self.checkEvents()
        self.checkCollisions()
        self.updateScreen()
        self.tick()
        pygame.event.pump()

    # these methods are meant to be overridden and have systems/processes ran in them
    def checkEvents(self):
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
    def checkCollisions(self):
        pass

    def updateScreen(self):
        pass

    def tick(self):
        self.clock.tick(60)

    def quit(self):
        self.done = True
        self.screen.fill((0,0,0))
        return self.next, self.paused

    def closeGame(self):
        sys.exit(0)
