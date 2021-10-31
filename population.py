from random import sample

from bot import Bot
from hyper_parameters import HyperParameters
from motion import Motion
from N_net_class import Network


class Population:
    def __init__(
        self,
        amount,
        net: Network = None,
        NN: list = [4, 6, 5, 5],  # NL=1, Nn=6, Ni=4, No=3
        hyper_parameters=HyperParameters(),
    ):
        self.amount = amount
        self.bots = []
        if net:
            for ibottype in range(amount):  # посев одного поколения ботов
                self.bots.append(
                    Bot(net=net, hyper_parameters=hyper_parameters, motion=Motion())
                )
        else:
            for ibottype in range(amount):  # посев одного поколения ботов
                self.bots.append(
                    Bot(NN=NN, hyper_parameters=hyper_parameters, motion=Motion())
                )


            # connectomes.append(bot_types[ibottype].N)

    def procreate(self, num_childs=10):
        child_bots = []
        n_champs = self.amount // num_childs
        self.define_n_champions(n_champs)
        for champion in self.champions:
            for j in range(num_childs):
                child = champion.make_child()
                child_bots.append(child)
        for _ in range(self.amount % num_childs): #добиваем остаток первым чемпионом чтобы потомков было amount
            child = self.champions[0].make_child()
            child_bots.append(child)
        self.bots = child_bots.copy()


    def import_from_file(self, filename):
        pass

    def export_to_file(self, filename):
        pass

    def define_n_champions(self, n):
        #self.champions = sample(self.bots, n) #случайный отбор
        sorted_bots = sorted(self.bots, key=lambda x: x.score, reverse=True)
        self.champions = sorted_bots[0:n]
        print(f"champions: {self.champions}")

    def import_champions(self):
        pass


