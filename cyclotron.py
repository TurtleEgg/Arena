import sys

sys.path.append("/home/Code/Arena/")
sys.path.append("/home/Code/Arena/tests/")

import multiprocessing as mp
from colorama import init, Fore, Back, Style
from matplotlib.pyplot import plot, show
from numpy import mean, random

from datetime import datetime
from enum import Enum, unique
from typing import Any, Dict, List, Set


from arena import Arena, Team
from bot import Bot
from hyper_parameters import HyperParameters
from motion import Motion
from N_net_class import Network
from plot import plot_round
from population import Population


TIME_FORMAT = "%d-%m-%Y %H:%M"
TO_MINUTES = 1 / 60

random.seed()
# Initializes Colorama
init(autoreset=True)


class Cyclotron:
    def __init__(
        self,
        hyper_parameters: HyperParameters = HyperParameters,
        num_teams = 100,
        num_champions = 10,
        num_tests = 100,
        num_steps = 50

    ):
        self.hyper_parameters = hyper_parameters
        self.num_teams = num_teams
        self.num_champions = num_champions
        self.num_childs = self.num_teams // self.num_champions
        self.num_bots_in_team = 4
        self.num_tests = num_tests
        self.num_steps = num_steps
        self.dt = 1 / self.num_steps

        self.champ_scores = []

    def get_start_population(self, input_file="", input_is_champions = True) -> None:

        if input_file:
            if input_is_champions:
                self.population = Population(0)
                self.population.import_from_file(input_file, input_is_champions = True)
                self.population.procreate(self.num_childs)
            else:
                self.population = Population(0)
                self.population.import_from_file(input_file, input_is_champions = False)
                self.num_teams = self.population.amount
        else:
            self.population = Population(self.num_teams)

    def export_population(self, output_file):
        self.population.export_to_file(output_file)

    def export_champions(self, output_file):
        self.population.export_champions(output_file)

    def grind(self, num_generations: int, dump_step=0):
        print(f"{datetime.now().strftime(TIME_FORMAT)} Cyclotron launched")
        for i in range(num_generations):
            tic = datetime.today()

            self.population.init_scores()
            print(f"\n{datetime.now().strftime(TIME_FORMAT)}: gen {i}")
            for bot in self.population.bots:
                output = mp.Queue()
                processes = [mp.Process(target=self.examine_bot, args=(bot, output)) for _ in range(self.num_tests)]
                for p in processes:
                    p.start()
                for p in processes:
                    p.join()

                score = [output.get() for p in processes]

                bot.add_score(mean(score))
                #print(f"bot_score = {bot.score:.4f}")
            self.population.define_n_champions(self.num_champions)

            for champion in self.population.champions:
                #    print(f"\nchampion: {champion}")
                print(f"champion score: {champion.score:.4f}")


            self.champ_scores.append(self.population.champions[0].score)

            if dump_step:
                if i % dump_step==0:
                    self.export_champions(f"population/{i+1:03d}gen_ch.dat")

            self.population.procreate(self.num_childs)

            toc = datetime.today()
            delta = toc - tic
            delta_s = delta.total_seconds()
            delta_min = delta_s * TO_MINUTES
            print(f"Time used: {delta_s:.1f}s or {delta_min:.1f}min")

        print(f"\n{datetime.now().strftime(TIME_FORMAT)}: \033[2;31;43m cyclotron finished \033[0;0m")

    def test_team(self, team) -> float:
        arena = Arena(team=team)
        for move in range(self.num_steps):
            arena.make_move(self.dt)
        # plot_round(arena)
        mean_score = sum([bot.score for bot in arena.team.bots]) / self.num_bots_in_team

        return mean_score

    def examine_bot(self, bot, output):
        team = Team(bot, self.num_bots_in_team)
        score = self.test_team(team)
        output.put(score)

    def showmatch(self):
        print(f"\n{datetime.now().strftime(TIME_FORMAT)}: showmatch")
        print(len(self.population.champions))
        print("Champions:")
        for i, champion in enumerate(self.population.champions):
            print(f"      {i+1:3d} / {len(self.population.champions):3d}")
            arena = Arena(team=Team(champion, self.num_bots_in_team))
            for move in range(self.num_steps):
                arena.make_move(self.dt)
            plot_round(arena)


"""
cycletron = Cyclotron(init_type)
cycletron.get_start_population()

cycletron.grind(3)
cycletron.showmatch()
"""
