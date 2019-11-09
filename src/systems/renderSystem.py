from . import entCompSys
class RenderSystem(entCompSys.System):
    def __init__(self,window,clearColor=(0,0,0)):
        self.window = window
        self.clearColor = clearColor

    def process(self):
        self.window.fill(self.clearColor)
        pygame.display.flip()
