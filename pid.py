import time
kp = 0.04
ki = 0.075
kd = 0.02

class PID:
    prevIntegral = 0
    prevError = 0
    windup = 10
    def regulate(self, target, current, dt):
        e = target-current
        P = kp*e
        I = self.prevIntegral + (ki*e)*dt
        D = (e - self.prevError)/dt
        print(self.windup)
        if (I > self.windup):
            I = self.windup
        if (I < -self.windup):
            I = -self.windup

        self.prevIntegral = I
        self.prevError = e
        return P + I + D*kd