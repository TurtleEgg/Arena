import sys
sys.path.append("/home/Code/Arena/")
sys.path.append("/home/Code/Arena/tests/")

from arena import Arena
from bot import Bot
from motion import Motion
from N_net_class import Network
from plot import plot_round

network = Network([1, 6, 6, 5])
team = []
for i in range(4):
    team.append(Bot(net=network, motion=Motion()))

arena = Arena(team=team)

dt = 0.1

for move in range(10):
    arena.make_move(dt)
    print(f"move: {move}" )
    for bot in arena.team:
        print(bot.score)

score_team = sum([bot.score for bot in arena.team])
print(f"team score: {score_team}")

plot_round(arena)