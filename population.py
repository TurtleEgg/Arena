import pickle
from typing import Any, Dict, List
import numpy as np

from bot import Bot
from motion import Motion
from N_net_class import Network


class Population:
    def __init__(
        self,
        amount,
        net: Network = None,
        NN: list = [4, 6, 5, 5],  # NL=1, Nn=6, Ni=4, No=3
    ):
        self.amount = amount
        self.bots = []
        self.champions = None
        self.NN = NN
        if net:
            for ibottype in range(amount):  # посев одного поколения ботов
                self.bots.append(
                    Bot(net=net, motion=Motion())
                )
        else:
            for ibottype in range(amount):  # посев одного поколения ботов
                self.bots.append(
                    Bot(NN=NN, motion=Motion())
                )


            # connectomes.append(bot_types[ibottype].N)

    def procreate(self, num_childs=10, hyper_parameters: Dict[str, Any]={"mut_rate": 0.05, "mut_type": 1}):
        child_bots = []
        if not self.champions:
            n_champs = self.amount // num_childs
            self.define_n_champions(n_champs)

        for champion in self.champions:
            for _ in range(num_childs):
                child = champion.make_child(hyper_parameters=hyper_parameters)
                child_bots.append(child)
        for _ in range(self.amount % num_childs): #добиваем остаток первым чемпионом чтобы потомков было amount
            print(self.champions)
            child = self.champions[0].make_child(hyper_parameters=hyper_parameters)
            child_bots.append(child)
        self.bots = child_bots.copy()

    def import_from_file(self, filename, input_is_champions = True):
        infile = open(filename, 'rb')
        if input_is_champions:
            self.champions = pickle.load(infile)
        else:
            self.bots = pickle.load(infile)
            self.amount = len(self.bots)
        infile.close()

    def export_to_file(self, filename):
        outfile = open(filename, 'wb')
        pickle.dump(self.bots, outfile)
        outfile.close()

    def define_n_champions(self, n):
        #self.champions = sample(self.bots, n) #случайный отбор
        sorted_bots = sorted(self.bots, key=lambda x: x.score, reverse=True)
        self.champions = sorted_bots[0:n]
        #print(f"champions: {self.champions}")

    def export_champions(self, filename):
        outfile = open(filename, 'wb')
        pickle.dump(self.champions, outfile)
        outfile.close()

    def init_scores(self):
        for bot in self.bots:
            bot.init_score()


