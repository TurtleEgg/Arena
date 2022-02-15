from copy import deepcopy
from typing import Any, Dict

from motion import Motion
from N_net_class import Network

TEAMMATE_COUNT = 3

class Bot:
    def __init__(
        self,
        net: Network = None,
        NN: list = [4, 6, 6, 5],  # NL=1, Nn=6, Ni=4, No=3
        motion=Motion(),
    ):
        self.motion = motion
        if net:
            self.net = net
        else:
            self.NN = NN
            self.net = Network(NN=self.NN)

        self.score = 0
        self.broadcasted = 0
        self.heared = 0
        self.is_in_place = False

        self.Out = list(range(self.net.No))
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
        heared_norm = self.heared/TEAMMATE_COUNT
        In = [
            self.motion.velocity,
            ground_type,
            heared_norm,
            self.Out[3],
            self.Out[4],
        ]
        # print(In)
        [VL, VR, self.broadcasted, Out1, Out2] = self.net.go(In)
        Out = [VL, VR, self.broadcasted, Out1, Out2]
        self.Out = Out.copy()
        self.motion.set_wheels({"left_wheel": Out[0], "right_wheel": Out[1]})
        self.motion.move(dt)

        self.heared = 0

        self.io_track.append({"ground_type": ground_type, "heared": heared_norm, "in": (Out[3], Out[4]), "broadcasted": self.broadcasted})

        return In, Out

    def make_child(self, hyper_parameters: Dict[str, Any]={"mut_rate": 0.05, "mut_type": 1}):
        child_net = deepcopy(self.net)
        child_net.mutate(hyper_parameters=hyper_parameters)
        child = Bot(net=child_net, motion=Motion())

        return child

    def add_score(self, delta_score):
        self.score += delta_score

    def init_score(self):
        self.score = 0

    def add_heared(self, heared):
        self.heared += heared

    def update_ground_type(self, is_in_place: bool):
        self.is_in_place = is_in_place
