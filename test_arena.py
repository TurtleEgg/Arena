import sys
sys.path.append("/home/Code/Arena/")
sys.path.append("/home/Code/Arena/tests/")

from arena import Arena, Team
from bot import Bot
from motion import Motion
from N_net_class import Network
from plot import plot_round

NN = [4, 6, 5, 5]
team = Team(Bot(NN=NN), 4)

arena = Arena(team=team)

dt = 0.1

for move in range(10):
    arena.make_move(dt)
    print(f"move: {move}" )
    for bot in arena.team.bots:
        print(bot.score)

score_team = sum([bot.score for bot in arena.team.bots])
print(f"team score: {score_team}")

plot_round(arena, annotation_step=5)