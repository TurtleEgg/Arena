import sys
sys.path.append("/home/Code/Arena/")
sys.path.append("/home/Code/Arena/tests/")

from arena import Arena, Team
from bot import Bot
from motion import Motion
from N_net_class import Network
from plot import plot_round

shape: dict = {
    "sensors": 2,
    "layers": 2,
    "inner neurons": 3,
    "inter neurons": 1,
    "motors": 2,
    "alphabet": 2,
}
team = Team(Bot(shape=shape), 4)

arena = Arena(team=team)

dt = 0.2

for move in range(5):
    arena.make_move(dt)
    print(f"move: {move}" )
    for bot in arena.team.bots:
        print(bot.score)

score_team = sum([bot.score for bot in arena.team.bots])
print(f"team score: {score_team}")

plot_round(arena, annotation_step=1)