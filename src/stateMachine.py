
# i'm actually quite happy with this though i'm thinking of branching it out in to a module to import
#to use as a generic fsm for things other than game states, like animation states and behaviors etc
class Engine:
    #a generic state mach
    def __init__(self):
        self.currentState = State()
        self.states = []

    def run(self):
        self.states = [self.currentState]
        while self.states:
            self.currentState = self.states.pop()
            if self.currentState.paused:
                self.currentState.unpause()

            next, paused = self.currentState.mainloop()
            if self.currentState.killPrev and self.states:
                self.states.pop()
            if paused:  #paused states are kept
                self.states.append(self.currentState)
            if next:
                self.states.append(next)

# state object
class State:
    def __init__(self):
        self.done = False
        self.next = None
        self.paused = False #is if it is or isn't paused
        self.killPrev = False #removes last state from states stack

    def reinit(self): # put things here that need to be ran after
        pass # the state has been returned to

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False
        self.done = False
        self.next = None

    def mainStart(self):
        pass

    def update(self):
        pass

# do not overwrite
    def mainloop(self):
        self.mainStart()
        while not self.done:
            self.update()
        return self.next,self.paused
