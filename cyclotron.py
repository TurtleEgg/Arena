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
from motion import Motion
from N_net_class import Network
from plot import plot_round
from population import Population
from hyper_parameters import update_hyper_parameters


TIME_FORMAT = "%d-%m-%Y %H:%M"
TO_MINUTES = 1 / 60

random.seed()
# Initializes Colorama
init(autoreset=True)


class Cyclotron:
    def __init__(
        self,
        hyper_parameters: Dict[str, Any] = {"mut_rate": 0.003, "mut_type": 1},
        num_teams=100,
        num_champions=10,
        num_tests=100,
        num_steps=50

    ):
        self.hyper_parameters = hyper_parameters
        self.num_teams = num_teams
        self.num_champions = num_champions
        self.num_childs = self.num_teams // self.num_champions
        self.num_bots_in_team = 4
        self.num_tests = num_tests
        self.num_steps = num_steps
        self.dt = 1 / self.num_steps
        self.NN = [4, 6, 5, 5]

        self.champ_scores = []

    def get_start_population(self, input_file=None, input_is_champions=True) -> None:

        if input_file:
            self.population = Population(0, NN=self.NN)
            self.population.import_from_file(input_file, input_is_champions=input_is_champions)

            if input_is_champions:
                self.population.procreate(self.num_childs, hyper_parameters=hyper_parameters)
            else:
                self.num_teams = self.population.amount
        else:
            self.population = Population(self.num_teams, NN=self.NN)

    def export_population_to_file(self, output_file):
        self.population.export_to_file(output_file)

    def export_champions_to_file(self, output_file):
        self.population.export_champions(output_file)

    def grind_es(self, num_generations: int, dump_step=0):
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
                # print(f"bot_score = {bot.score:.4f}")
            self.population.define_n_champions(self.num_champions)

            for champion in self.population.champions:
                #    print(f"\nchampion: {champion}")
                print(f"champion score: {champion.score:.4f}")
            self.champ_scores.append(self.population.champions[0].score)

            if dump_step:
                if (i + 1) % dump_step == 0:
                    self.export_champions_to_file(f"population/{i + 1:03d}gen_ch.dat")

            scores = [bot.score for bot in self.population.bots]
            self.hyper_parameters = update_hyper_parameters(self.hyper_parameters, scores=scores)

            self.population.procreate(self.num_childs, hyper_parameters=self.hyper_parameters)

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

    def showmatch(self, index=None):
        print(f"\n{datetime.now().strftime(TIME_FORMAT)}: showmatch")
        print(len(self.population.champions))
        print("Champions:")
        if index:
            champions = [self.population.champions[index - 1]]
        else:
            try:
                champions = self.population.champions
            except (IndexError, TypeError):
                raise Exception("Wrong index.")
        for i, champion in enumerate(champions):
            print(f"      {i + 1:3d} / {len(self.population.champions):3d}")
            arena = Arena(team=Team(champion, self.num_bots_in_team))
            for _ in range(self.num_steps):
                arena.make_move(self.dt)
            plot_round(arena)


"""
cycletron = Cyclotron(init_type)
cycletron.get_start_population()

cycletron.grind(3)
cycletron.showmatch()
"""
