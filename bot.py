import sys

sys.path.append("/home/Code/Arena/")
sys.path.append("/home/Code/Arena/tests/")

from bot import Bot

shape: dict = {
    "sensors": 2,
    "layers": 2,
    "inner neurons": 3,
    "inter neurons": 1,
    "motors": 2,
    "alphabet": 2,
}
bot = Bot(shape=shape)

print(bot.motion.pos)
bot.move(0.1)
print(bot.motion.pos)
bot.move(0.1)
bot.move(0.1)

from population import Population

pop = Population(4,shape=shape)
Nm1 = pop.bots[0].net.Wi.copy()

for individual in pop.bots:
    print(individual.motion.pos)
    # print(individual.net.Wi)
    # print(individual.net.Wo)
    # print(individual.net.W)

pop.procreate(num_childs=2)

for individual in pop.bots:
    print(individual.motion.pos)
    # print(individual.net.Wi)
    # print(individual.net.Wo)
    # print(individual.net.W)


Nm2 = pop.bots[0].net.Wi.copy()
# print(Nm1)
# print(Nm2)
print("mutation matrix:")
print(Nm2 - Nm1)
