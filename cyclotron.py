import sys

sys.path.append("/home/Code/Arena/")
sys.path.append("/home/Code/Arena/tests/")

from matplotlib.pyplot import plot, show
from numpy import mean, random

import datetime
from enum import Enum, unique
from typing import Any, Dict, List, Set


from arena import Arena, Team
from bot import Bot
from hyper_parameters import HyperParameters
from motion import Motion
from N_net_class import Network
from plot import plot_round
from population import Population

random.seed()


class InitType(Enum):
    GENERATE = 0
    FROM_CHAMPS = 1
    POPULATION = 2


class Cyclotron:
    def __init__(
        self,
        init_type: InitType = InitType.GENERATE,
        input_file: str = None,
        output_file: str = None,
        hyper_parameters: HyperParameters = HyperParameters,
        num_teams = 50,
        num_champions = 5,
        num_tests = 80,
        num_steps = 50

    ):
        self.init_type = init_type
        if input_file:
            self.input_file = input_file
        if output_file:
            self.output_file = output_file
        self.hyper_parameters = hyper_parameters

        self.num_teams = num_teams
        self.num_champions = num_champions
        self.num_childs = self.num_teams // self.num_champions
        self.num_bots_in_team = 4
        self.num_tests = num_tests
        self.num_steps = num_steps
        self.dt = 1 / self.num_steps

        self.champ_scores = []

    def get_start_population(self, filename=None) -> Population:

        if self.init_type == InitType.GENERATE:
            self.population = Population(self.num_teams)

        if self.init_type == InitType.POPULATION:
            gen0 = Population()
            self.population = gen0.import_from_file(filename)

        if self.init_type == InitType.FROM_CHAMPS:
            gen0 = Population()
            gen0.import_from_file(filename)
            self.population = gen0.procreate(self.num_childs)

    def grind(self, num_generations: int):
        now = datetime.datetime.now()
        print(now.strftime("%d-%m-%Y %H:%M"), "Cyclotron launched")
        for i in range(num_generations):
            now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
            print(f"\n{now}: gen {i}")
            for bot in self.population.bots:
                score = []
                for _ in range(self.num_tests):
                    team = Team(bot, self.num_bots_in_team)
                    score.append(self.test_team(team))
                bot.add_score(mean(score))
                #print(f"bot_score = {bot.score:.4f}")
            self.population.define_n_champions(self.num_champions)

            for champion in self.population.champions:
                #    print(f"\nchampion: {champion}")
                print(f"champion score: {champion.score:.4f}")

            self.champ_scores.append(self.population.champions[0].score)

            self.population.procreate(self.num_childs)
            # print(f"\npopulation: {self.population.bots}")
            # print(f"champions: {self.population.champions}")

    def test_team(self, team) -> float:
        arena = Arena(team=team)
        for move in range(self.num_steps):
            arena.make_move(self.dt)
        # plot_round(arena)
        mean_score = sum([bot.score for bot in arena.team.bots]) / self.num_bots_in_team

        return mean_score

    def showmatch(self):
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        print(f"\n{now}: showmatch")
        print(len(self.population.champions))
        for champion in self.population.champions:
            print(champion)
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
