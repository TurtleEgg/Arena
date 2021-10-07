from Bot import Bot
from hyper_parameters import HyperParameters
from motion import Motion
from N_net_class import network

class Population():
    def __init__(self, amount, net: network = None,
        NN: list = [4, 6, 6, 5],  # NL=1, Nn=6, Ni=4, No=3
        hyper_parameters=HyperParameters(),
        motion=Motion() ):
        for ibottype in range(amount):  # посев одного поколения ботов
            bot_types.append(Bot(**kwargs))
            connectomes.append(bot_types[ibottype].N)

    def procreate(self, num_childs, mut_type, mut_rate):
        pass

    def import_from_file(self, filename):
        pass

    def export_to_file(self, filename):
        pass

    def champions(self):
        pass