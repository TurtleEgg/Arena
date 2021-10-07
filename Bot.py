from hyper_parameters import HyperParameters
from motion import Motion
from N_net_class import network

class Bot:
    def __init__(
        self,
        net: network = None,
        NN: list = [4, 6, 6, 5],  # NL=1, Nn=6, Ni=4, No=3
        hyper_parameters=HyperParameters(),
        motion=Motion(),
    ):
        self.motion = motion
        if net:
            self.N = net
        else:
            self.NN = NN
            self.net = network(NN=self.NN, hyper_parameters=hyper_parameters)

        self.Out = list(range(self.NN[2]))

    def move(self, dt, ground_type, sound_level):
        # промежуток времени - постоянный
        # print("groundtype: ", grtype)
        In = [
            self.motion.vel["x"],
            self.motion.vel["y"],
            ground_type,
            soundlevel,
            self.N_Out[3],
            self.N_Out[4],
        ]
        # print(In)
        [VL, VR, sound, Out1, Out2] = self.N.go(In)
        Out = [VL, VR, sound, Out1, Out2]
        self.N_Out = Out.copy()
        self.motion.set_wheels({"left_wheel": Out[0], "right_wheel": Out[1]})
        self.motion.move(dt)
        return In, Out

    def make_child(self):
        child_net = self.net.mutate()
        child = Bot(net=child_net)
        return child
