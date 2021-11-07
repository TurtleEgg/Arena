from matplotlib.pyplot import gca, Circle, scatter, show, subplot

from arena import Arena, Place
from bot import Bot
from motion import Motion
from N_net_class import Network

from cycler import cycler
COLORS = ['blue', 'green', 'red', 'yellow'] #['r','b','m','g']
custom_cycler = (cycler(color=COLORS))


def plot_round(arena, annotation_step:int=10):
    subplot(1,2,1)
    ax = gca()
    for place in arena.places:
        circle = Circle((place.coor[0], place.coor[1]), place.r, color="r", fill=False)
        ax.add_patch(circle)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_prop_cycle(custom_cycler)

    for i, bot in enumerate(arena.team.bots):
        x = [motion_record.pos["x"] for motion_record in bot.motion_track]
        y = [motion_record.pos["y"] for motion_record in bot.motion_track]
        scatter(x[0], y[0])
        ax.plot(x, y)

        for i, record in enumerate(zip(bot.motion_track, bot.io_track)):
            if i % annotation_step==0:
                motion_record, io_record = record
                _plot_info(ax, motion_record, io_record)

    for i, bot in enumerate(arena.team.bots):
        heared = [io_record["heared"] for io_record in bot.io_track]
        broadcasted = [io_record["broadcasted"] for io_record in bot.io_track]
        subplot(4, 2, i*2+2)
        sp = gca()
        sp.set_ylim([-2, 2])
        sp.plot(heared, label="h")
        sp.plot(broadcasted, label="b")
        sp.legend(loc='best')
        sp.title(COLORS[i])


    show()

def _plot_info(subplot, motion_record: dict, io_record: dict):
    ground_type = io_record["ground_type"]
    heared = io_record["heared"]
    broadcasted = io_record["broadcasted"]
    annotation = f"gr: {ground_type:d}\nh: {heared:0.2f}\nb: {broadcasted:0.2f}"
    x_i = motion_record.pos["x"]
    y_i = motion_record.pos["y"]
    subplot.annotate(annotation, (x_i, y_i))

def _plot_voices(subplot, ):
    pass

def plot_net():
    pass
