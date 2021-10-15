import numpy as np
import math
import numpy.random as rand
from numpy import array

from bot import Bot
from hyper_parameters import HyperParameters
from motion import Motion
from N_net_class import Network


def sum_of_squares(v):
    """ v1 * v1 + v2 * v2 ... + vn * vn"""
    # или return dot_product(v, v)
    return sum(vi ** 2 for vi in v)


def magnitude(v):
    return math.sqrt(sum_of_squares(v))

GUESTS_SCORE_MAP = (0, 1, 2, -1, -2)

class Place():
    def __init__(self, coor: np.array, r=0.2):
        self.x = coor[0]
        self.y = coor[1]
        self.r = r
        self.score = 0
        self.guests_number = 0

    @static
    def update_score(self, dt: float) -> None:
        self.score += dt * GUESTS_SCORE_MAP[self.guests_number]

    def update_guest(self, bot: Bot) -> None:
        is_guest = self._test_guest(bot.motion)
        if is_guest:
            self.guests_number += 1

    def _test_guest(self, motion: Motion):
        bot_coor = array( [motion.pos["x"], motion.pos["y"]] )
        if magnitude(self.coor - bot_coor) < self.r:
            return True
        else:
            return False



class Field(object):
    def __init__(self, net=Network([4, 6, 6, 5])):
        self.place1 = Place(np.array([0.25, 0.75]), r=0.2)
        self.place2 = Place(np.array([0.75, 0.25]), r=0.2)
        self.noisemakers = []
        self.score = 0

    def move(self, dt):
        # размер пятна постоянный
        R = 0.2
        sc_sing = 1
        sc_bi = 2
        sc_tri = -1
        sc_quat = -2
        addscore = 0
        S1 = []
        S2 = []
        for Xi, Yi, leveli in self.noisemakers:
            S1.append(magnitude([Xi, Yi] - self.X1))
            S2.append(magnitude([Xi, Yi] - self.X2))
        count1 = 0
        count2 = 0
        for s in S1:
            if s < R:
                count1 += 1
        for s in S2:
            if s < R:
                count2 += 1

        if count1 == 1:
            addscore += sc_sing * dt
        elif count1 == 2:
            addscore += sc_bi * dt
        elif count1 == 3:
            addscore += sc_tri * dt
        elif count1 == 4:
            addscore += sc_quat * dt
        if count2 == 1:
            addscore += sc_sing * dt
        elif count2 == 2:
            addscore += sc_bi * dt
        elif count2 == 3:
            addscore += sc_tri * dt
        elif count2 == 4:
            addscore += sc_quat * dt
        self.score += addscore

        self.noisemakers = []

    def placenoisemaker(self, X, Y, level):
        self.noisemakers.append((X, Y, level))
        # print("noisemaker placed: ",X,Y,level )

    def soundlevel(self, Coor, V):
        X = Coor[0]
        Y = Coor[1]
        Vx = V[0]
        Vy = V[1]
        level = 0
        # когда смотришь прямо на звук, коэффициент сигнала1, когда спиной - 0
        for Xi, Yi, leveli in self.noisemakers:
            S = magnitude([X - Xi, Y - Yi])
            if S != 0:
                # единичный вектор направления от источника к слушателю
                n = np.array([(X - Xi) / S, (Y - Yi) / S])
                li = np.dot([Vx, Vy], n)
                if li > 0:
                    level = +li
        return level

    def groundtype(self, Coor=[0.25, 0.75]):
        Coor = np.array(Coor)

        # размер пятна постоянный
        R = 0.2
        if magnitude(Coor - self.X1) < R or magnitude(Coor - self.X2) < R:
            return 1
        else:
            return 0



