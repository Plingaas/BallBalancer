import numpy as np

a1 = 50
a2 = 87.87

def computeLength(x, y):
    return np.sqrt(x**2 + y**2)


def computeAngle(disp):
    r = np.sqrt(disp[0] ** 2 + disp[1] ** 2)  # Eq. 1
    phi1 = np.arctan2(disp[1], disp[0])  # Eq. 2
    phi2 = np.arccos((a2**2 - a1**2 - r**2) / (-2 * a1 * r))  # Eq. 3
    return phi1 - phi2


def deg2step(deg):
    return int((deg + 30) * 8.89)


def rad2step(rad):
    return deg2step(np.rad2deg(rad))



def getAngles(pitch, roll):
    H = 80.0
    L = H * np.sqrt(3)
    z = 12
    Ppr1 = [
        (L / 2) * np.cos(roll) - (L / (2 * np.sqrt(3))) * np.sin(pitch) * np.sin(roll),
        (L / (2 * np.sqrt(3))) * np.cos(pitch),
        (L / 2) * np.sin(roll)
        + (L / (2 * np.sqrt(3))) * np.sin(pitch) * np.cos(roll)
        + z,
    ]

    Ppr2 = [
        -(L / 2) * np.cos(roll) - (L / (2 * np.sqrt(3))) * np.sin(pitch) * np.sin(roll),
        (L / (2 * np.sqrt(3))) * np.cos(pitch),
        -(L / 2) * np.sin(roll)
        + (L / (2 * np.sqrt(3))) * np.sin(pitch) * np.cos(roll)
        + z,
    ]

    Ppr3 = [
        (L / np.sqrt(3)) * np.sin(pitch) * np.sin(roll),
        -(L / np.sqrt(3)) * np.cos(pitch),
        -(L / np.sqrt(3)) * np.sin(pitch) * np.cos(roll) + z,
    ]

    a2 = 87.87

    M1 = [15 * np.sqrt(3), 15, -a2]
    M2 = [-15 * np.sqrt(3), 15, -a2]
    M3 = [0, -30, -a2]

    P1_Len = computeLength(Ppr1[0] - M1[0], Ppr1[1] - M1[1])
    P2_Len = computeLength(Ppr2[0] - M2[0], Ppr2[1] - M2[1])
    P3_Len = computeLength(Ppr3[0] - M3[0], Ppr3[1] - M3[1])

    m1disp = [P1_Len, Ppr1[2] - M1[2]]
    m2disp = [P2_Len, Ppr2[2] - M2[2]]
    m3disp = [P3_Len, Ppr3[2] - M3[2]]

    theta1 = computeAngle(m1disp)# + 32 # 32, 28, 29.6 physically calibrated
    theta2 = computeAngle(m2disp)# + 38
    theta3 = computeAngle(m3disp)# + 29.6

    return [np.rad2deg(theta1), np.rad2deg(theta2), np.rad2deg(theta3)]

def getPitch(dy): # y position gives how much pitch
    return -dy

def getRoll(dx): # x position gives how much roll
    return -dx