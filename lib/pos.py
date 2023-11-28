import numpy as np

class Position:
    mult = 0.8
    target = (0,0)
    t = 0
    def update(self, dt):
        self.t += dt


        
        if (self.t < 5):
            self.target = (0,0)
        
        if (self.t >= 5 and self.t < 15):
            self.target = (np.cos(self.t*2.5)*130, np.sin(self.t*2.5)*130)

        if (self.t >= 15 and self.t < 17):
            self.target = (225*self.mult, 0)
        
        if (self.t >= 17 and self.t < 19):
            self.target = (113*self.mult, 195*self.mult)
        
        if (self.t >= 19 and self.t < 21):
            self.target = (-113*self.mult, 195*self.mult)

        if (self.t >= 21 and self.t < 23):
            self.target = (-225*self.mult, -0)
        
        if (self.t >= 23 and self.t < 25):
            self.target = (-113*self.mult, -195*self.mult)
        
        if (self.t >= 25 and self.t < 27):
            self.target = (113*self.mult, -195*self.mult)
        
        if (self.t >= 27 and self.t < 29):
            self.target = (225*self.mult, 0)
        
        if (self.t >= 29):
            self.t -= 29
        
        