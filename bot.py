from hyper_parameters import HyperParameters
from motion import Motion
from N_net_class import Network

class Bot:
    def __init__(
        self,
        net: Network = None,
        NN: list = [4, 6, 6, 5],  # NL=1, Nn=6, Ni=4, No=3
        hyper_parameters=HyperParameters(),
        motion=Motion(),
    ):
        self.motion = motion
        if net:
            self.net = net
        else:
            self.NN = NN
            self.net = Network(NN=self.NN, hyper_parameters=hyper_parameters)

        self.score = 0
        self.Out = list(range(self.net.No))

    def move(self, dt, ground_type, sound_level):
        # промежуток времени - постоянный
        # print("groundtype: ", grtype)
        In = [
            self.motion.vel["x"],
            self.motion.vel["y"],
            ground_type,
            sound_level,
            self.Out[3],
            self.Out[4],
        ]
        # print(In)
        [VL, VR, sound, Out1, Out2] = self.net.go(In)
        Out = [VL, VR, sound, Out1, Out2]
        self.Out = Out.copy()
        self.motion.set_wheels({"left_wheel": Out[0], "right_wheel": Out[1]})
        self.motion.move(dt)

        return In, Out

    def make_child(self):
        child_net = self.net
        child_net.mutate()
        child = Bot(net=child_net, motion=Motion())

        return child

    def update_score(self, score):
        self.score = score
