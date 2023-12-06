kp = 0.09
ki = 0.05
kd = 0.08

class PID:
    prevIntegral = 0
    prevError = 0
    windup = 10
    def regulate(self, target, current, dt):
        e = target-current

        P = kp*e
        I = self.prevIntegral + (ki*e)*dt
        D = (e - self.prevError)/dt
        if (I > self.windup):
            I = self.windup
        if (I < -self.windup):
            I = -self.windup

        self.prevIntegral = I
        self.prevError = e

        return P + I + D*kd