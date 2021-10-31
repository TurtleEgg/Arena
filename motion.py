import math
from numpy import array, cos, sin
from random import uniform

def sum_of_squares(v):
    """v1 * v1 + v2 * v2 ... + vn * vn"""
    # или return dot_product(v, v)
    return sum(vi ** 2 for vi in v)

def magnitude(v):
    return math.sqrt(sum_of_squares(v))

class Motion():

    # коэффициент преобразования момента на моторе в ускорение
    K_MOT = 0.1
    # ширина колесной пары
    H = 0.5

    def __init__(
        self,
        pos=None,
        t=None, #вектор направления
        vel=None,
        m_wheels=None,
    ):
        if pos:
            self.pos = pos
        else:
            x = uniform(0, 1)
            y = uniform(0, 1)
            self.pos = {"x": x, "y": y}
        if vel:
            self.vel = vel
        else:
            x = uniform(-1, 1)
            y = uniform(-1, 1)
            self.vel = {"x": x, "y": y}
        if m_wheels:
            self.m_wheels = m_wheels
        else:
            x = uniform(-1, 1)
            y = uniform(-1, 1)
            self.m_wheels = {"right_wheel": x, "left_wheel": y}
        if t:
            self.t = t
        else:
            x = uniform(-1, 1)
            y = uniform(-1, 1)
            self.t = {"x": x, "y": y}

        V = array([self.vel["x"], self.vel["y"]])
        self.velocity = magnitude(V)



    def set_wheels(self, m_wheels):
        self.m_wheels = m_wheels

    def move(self, dt):
        X = self.pos["x"]
        Y = self.pos["y"]
        VR = self.m_wheels["right_wheel"]
        VL = self.m_wheels["left_wheel"]
        V = array([self.vel["x"], self.vel["y"]])
        fi = array([self.t["x"], self.t["y"]])
        # print("V:", V)
        X += V[0] * dt
        Y += V[1] * dt
        # коэффициент преобразования момента на моторе в ускорение
        k_mot = self.K_MOT
        # ширина колесной пары
        H = self.H
        dfi = k_mot * (VR - VL) / H
        v1_new = (V[0] * cos(dfi)) - (V[1] * sin(dfi))
        v2_new = (V[1] * cos(dfi)) + (V[0] * sin(dfi))
        V = array([v1_new, v2_new])
        if magnitude(V) != 0:
            fi = V / magnitude(V)
        self.fi = fi
        dV = k_mot * (VL + VR) / 2
        V = dV * fi + V
        if X > 1:
            X = 1
            V[0] = -V[0]
        elif X < 0:
            X = 0
            V[0] = -V[0]
        if Y > 1:
            Y = 1
            V[1] = -V[1]
        elif Y < 0:
            Y = 0
            V[1] = -V[1]
        self.V = V
        self.vel["x"] = V[0]
        self.vel["y"] = V[1]
        self.velocity = magnitude(V)
        self.pos["x"] = X
        self.pos["y"] = Y
