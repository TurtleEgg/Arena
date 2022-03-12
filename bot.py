from copy import deepcopy
from typing import Any, Dict
from random import random

import numpy as np

from motion import Motion
from N_net_class import Network


class Bot:
    def __init__(
        self,
        net: Network = None,
        shape: dict = {
            "sensors": 3,
            "layers": 4,
            "inner neurons": 6,
            "inter neurons": 6,
            "motors": 2,
            "alphabet": 5,
        },
        motion=Motion(),
    ):
        self.motion = motion
        if net:
            self.net = net
        else:
            self.NN = {
                "layers": shape["layers"],
                "inner neurons": shape["inner neurons"],
                "input neurons": shape["sensors"]
                                 + shape["inter neurons"]
                                 + 2 * shape["alphabet"],
                "output neurons": shape["motors"]
                                  + shape["inter neurons"]
                                  + shape["alphabet"],
            }
            self.net = Network(NN=self.NN)

        self.output = {
            "left_wheel": 0,
            "right_wheel": 0,
            "inter neurons": [random() for _ in range(shape["inter neurons"])],
            "broadcasted": [random() for _ in range(shape["alphabet"])],
        }
        self.score = 0
        self.broadcasted = np.zeros(shape["alphabet"])
        self.heared = np.zeros(shape["alphabet"])
        self.is_in_place = False

        self.motion_track = []
        self.io_track = []

    def move(self, dt):
        motion_record = deepcopy(self.motion)
        self.motion_track.append(motion_record)

        # промежуток времени - постоянный
        if self.is_in_place:
            ground_type = 1
        else:
            ground_type = 0
        input = [
            self.motion.velocity,
            ground_type,
        ]
        input.extend(self.heared)
        input.extend(self.output["inter neurons"])
        input.extend(self.output["broadcasted"])
        out_raw = self.net.go(input)
        output = {
            "left_wheel": out_raw[0],
            "right_wheel": out_raw[1],
            "inter neurons": out_raw[2: 2 + self.shape["inter neurons"]],
            "broadcasted": self._broadcast_one_hot(out_raw[2 + self.shape["inter neurons"]:
                                                           2 + self.shape["inter neurons"] + self.shape["alphabet"]]),
        }
        self.output = output.copy()
        self.motion.set_wheels({"left_wheel": output["left_wheel"], "right_wheel": output["right_wheel"]})
        self.motion.move(dt)

        self.heared = np.zeros(self.shape["alphabet"])

        self.io_track.append({"heared": self.heared, "ground_type": ground_type, "velocity": self.motion.velocity,
                              "output": self.output})

        return

    @staticmethod
    def _broadcast_one_hot(broadcasted_raw):
        result = np.zeros(len(broadcasted_raw))
        ind_max = np.argmax(broadcasted_raw)
        result[ind_max] = 1

        return result

    def make_child(
            self, hyper_parameters: Dict[str, Any] = {"mut_rate": 0.05, "mut_type": 1}
    ):
        child_net = deepcopy(self.net)
        child_net.mutate(hyper_parameters=hyper_parameters)
        child = Bot(net=child_net, shape=self.shape, motion=Motion())

        return child

    def add_score(self, delta_score):
        self.score += delta_score

    def init_score(self):
        self.score = 0

    def add_heared(self, heared):
        self.heared += heared

    def update_ground_type(self, is_in_place: bool):
        self.is_in_place = is_in_place