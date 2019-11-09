#okay for the record any time pygame gets imported use the
#specific module unless you want the alsa overrun error
import pygame.image
class Image:
    def __init__(self,filename,sheet=False):
        if not sheet:
            self.frame = pygame.image.load("/home/jym/Desktop/dev/Ghreti/img/"+filename)
