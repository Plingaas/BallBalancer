kp = 60
ki = 150
kd = 35

class PID:
    prevIntegral = 0
    prevError = 0
    windup = 2
    def regulate(self, target, current, dt):
        e = target-current

        
        P = kp*e*0.001
        I = self.prevIntegral + (ki*e*0.001)*dt
        D = (e - self.prevError)/dt
    
        if (I > self.windup):
            I = self.windup
        if (I < -self.windup):
            I = -self.windup
        
        self.prevIntegral = I
        self.prevError = e

        return P + I + D*kd*0.001