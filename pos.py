import numpy as np

class Position:
    mult = 0.8
    target = (0,0)
    t = 0
    spd = 1
    def update(self, dt):
        self.t += dt
        #self.target = (100*np.sin(self.t*2), 100*np.cos(self.t*2))
        