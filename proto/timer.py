
#-----
#Timer
#-----
class Timer:
    def __init__(self,length):
        self.count = 0
        self.length = length
        self.active = True
    def updating(self):
        if not self.active:
            return None
        if self.count < self.length:
            self.count += 1
        if self.count >= self.length:
            self.count = 0
            return True
        return False
    def setLength(self,value):
        self.length = value
    def deactivate(self):
        self.active = False
    def activate(self):
        self.count = 0
        self.active = True
