import numpy as np
import math
import numpy.random as rand

from copy import deepcopy
from itertools import combinations
from typing import List
from numpy import array

from bot import Bot
from motion import Motion
from N_net_class import Network


def sum_of_squares(v):
    """ v1 * v1 + v2 * v2 ... + vn * vn"""
    # или return dot_product(v, v)
    return sum(vi ** 2 for vi in v)


def magnitude(v):
    return math.sqrt(sum_of_squares(v))

RESIDENTS_SCORE_MAP = (0, 1, 1.1, -0.33, -0.25, -0.2, -0.17, -0.14, -0.125)
MAX_HEARING_DISTANCE = 1


class Team():
    def __init__(self, bot, amount):
        net = deepcopy(bot.net)
        bots = []
        for _ in range(amount):
            bots.append(Bot(net=net, shape=bot.shape, motion=Motion()))
        self.bots = bots

class Place:
    def __init__(self, coor: np.array, r=0.2):
        self.coor = coor
        self.r = r
        self.score = 0
        self.residents_count = 0

    def reinit_residents_count(self):
        self.residents_count = 0

    def update_resident(self, motion: Motion) -> bool:
        is_resident = self.test_resident(motion)
        if is_resident:
            self.residents_count += 1

        return is_resident

    def test_resident(self, motion: Motion) -> bool:
        bot_coor = array( [motion.pos["x"], motion.pos["y"]] )
        distance = magnitude(self.coor - bot_coor)
        if distance < self.r:
            return True
        else:
            return False


class Arena(object):
    def __init__(self, team: Team, feeder_params={"r": 0.2, "coors": [(0.25, 0.75), (0.75, 0.25), (0.25, 0.25), (0.75, 0.75)]},):
        self.team = team
        self.r = feeder_params["r"]
        self.places = [Place(np.array(coors), r=self.r) for coors in feeder_params["coors"]]

        self.score = 0

    def make_move(self, dt):
        #обнулить счетчики количества
        for place in self.places:
            place.reinit_residents_count()
        # вычисляем is_in_place заодно записываем в месте количество резидентов
        for bot in self.team.bots:
            bot.update_ground_type(False)
            for place in self.places:
                is_resident = place.update_resident(bot.motion)
                if is_resident:
                    bot.update_ground_type(is_resident)

        # обеспечиваем слышимость
        for bot1, bot2 in combinations(self.team.bots, 2):
            bot1.add_heared(np.multiply(bot2.output["broadcasted"], self._calc_heared_coeff(bot2.motion, bot1.motion)))
            bot2.add_heared(np.multiply(bot1.output["broadcasted"], self._calc_heared_coeff(bot1.motion, bot2.motion)))

        # движение ботов
        for bot in self.team.bots:
            bot.move(dt)
        #добавляем очки
        for bot in self.team.bots:
            for place in self.places:
                if place.test_resident(bot.motion):
                    delta_score = dt * RESIDENTS_SCORE_MAP[place.residents_count]
                    bot.add_score(delta_score)

    def _calc_heared_coeff(self, motion1: Motion, motion2: Motion) -> float:
        """Слышимость от первого ко второму.
        Зависит только от направления, не от расстояния.
        Когда смотришь прямо на звук, коэффициент сигнала 1, когда спиной - 0.
        Когда стоишь на месте - слышишь всё.
        Когда расстояние равно нулю - слышишь всё независимо от направления.
        """
        x1 = motion1.pos["x"]
        y1 = motion1.pos["y"]
        x2 = motion2.pos["x"]
        y2 = motion2.pos["y"]
        v_x = motion2.vel["x"]
        v_y = motion2.vel["y"]

        # когда смотришь прямо на звук, коэффициент сигнала 1, когда спиной - 0
        S = magnitude([x2 - x1, y2 - y1])
        if S >= MAX_HEARING_DISTANCE:
            pr = 0
            coeff = 0

        elif S > 0:

            k_s = MAX_HEARING_DISTANCE - S
            # единичный вектор направления от источника к слушателю
            n = np.array([(x2 - x1) / S, (y2 - y1) / S])
            # единичный вектор направления взгляда
            V = magnitude([v_x, v_y])
            if V != 0:
                e_v = np.array([v_x / V, v_y / V])
                pr = np.dot(e_v, n)
                coeff = 0.5 + pr / 2
            else:
                pr = 0
                coeff = 1

            coeff = coeff * k_s

        else:
            pr = 0
            coeff = 1

        return coeff
