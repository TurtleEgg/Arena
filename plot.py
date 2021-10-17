from matplotlib.pyplot import gca, Circle, scatter, show

from arena import Arena, Place
from bot import Bot
from motion import Motion
from N_net_class import Network

def plot_round(arena):
    ax = gca()
    for place in arena.places:
        circle = Circle((place.coor[0], place.coor[1]), place.r, color="r", fill=False)
        ax.add_patch(circle)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    for i, bot in enumerate(arena.team):
        x = [motion_record.pos["x"] for motion_record in bot.motion_track]
        y = [motion_record.pos["y"] for motion_record in bot.motion_track]
        scatter(x[0], y[0])
        ax.plot(x, y)

    show()
