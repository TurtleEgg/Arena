from enum import Enum, unique
from typing import Any, Dict, List, Set, int

import maroccolib as mc
import numpy as np
import math
import numpy.random as rand
import matplotlib.pyplot as plt
from N_net_class import network
import datetime
import pandas as pd

from maroccolib import field, bot, round, plot_round, Population

import csv
OUTPUT_FILENAME = "file_V_NL4.csv"

rand.seed()

class InitType(Enum):
    GENERATE = 0
    FROM_CHAMPS = 1
    POPULATION = 2


# 0 - generate randomly
# 1 - retrieve champions from file and mutate childs
# 2 - retrieve population from file
init_type = InitType.GENERATE
input_file_name= "BestPoints_NL4_8gen.csv"
NN = [4, 6, 6, 5]
W_start, W_end, B_start, B_end, Wi_start, Wi_end, Bi_start, Bi_end, Wo_start, Wo_end, Bo_start, numParams=mc.numParams(NN)
num_steps = 100
dt = 1 / num_steps
num_bots = 4
initial_num_types = 10*numParams*2
num_champions=10
#num_childs = numParams*2 # per each champion
num_childs = 100
print("num_childs: ", num_childs)
num_tries = 80 # количество испытаний одного бота - испытано в test_mean для num_steps = 100
num_gens = 3  # количество поколений
mutType =1
mutRate=0.03
step_interval = 3

genMeanScores = []
ConnectomesHistory = []
BotTypeHystory = []
champs=[]
rows=[]
now = datetime.datetime.now()
print(now.strftime("%d-%m-%Y %H:%M"), "Arena started")

def get_start_population(init_type: InitType, amount: int, filename=None) -> Population:
    gen0 = Population()

    if init_type == InitType.GENERATE:
        return gen0.generate(amount)

    if init_type == InitType.POPULATION:
        gen0.import_from_file(filename)
        return gen0

    if init_type == InitType.FROM_CHAMPS:
        gen0.import_from_file(filename)
        return gen0.generate(amount)


hyper_par = HyperParameters(mut_rate, step_interval)

for j in range(num_gens):
    hyper_par.update_rate(step = j)
    print("mut_rate: ", hyper_par.mut_rate)
    bots = []

    # инициализация ботов
    population = get_start_population(ini)

    bot_types = []
    connectomes = []
    meanScores = []



    if j == 0:
        if FIRST_GEN_GET_FROM == 0: #случайная генерация
            actual_num_types = initial_num_types
            for ibottype in range(actual_num_types):  # посев одного поколения ботов
                bot_types.append(bot( NN=NN, mutRate=mutRate))
                connectomes.append(bot_types[ibottype].N)
        else: #чтение из файла
            inputConnectomes = mc.readChamps(input_file_name, NN)
            actual_num_types = len(inputConnectomes)
            for ibottype in range(actual_num_types):
                bot_types.append(bot( NN=NN, mutRate=mutRate))
                bot_types[ibottype].N.W = inputConnectomes[ibottype].W.copy()
                bot_types[ibottype].N.B = inputConnectomes[ibottype].B.copy()
                bot_types[ibottype].N.Wi = inputConnectomes[ibottype].Wi.copy()
                bot_types[ibottype].N.Bi = inputConnectomes[ibottype].Bi.copy()
                bot_types[ibottype].N.Wo = inputConnectomes[ibottype].Wo.copy()
                bot_types[ibottype].N.Bo = inputConnectomes[ibottype].Bo.copy()
                connectomes.append(bot_types[ibottype].N)

    else: #derive from previous generation

        if FIRST_GEN_GET_FROM == 0:
            actual_num_types=num_champions*num_childs
        else:
            if j == 1:
                actual_num_types =len(champs) *num_childs
            else:
                actual_num_types = num_champions * num_childs

        for ibottype in range(actual_num_types):  # посев одного поколения ботов

            bot_types.append(bot( NN=NN, mutRate=mutRate))
            #мутируем чемпионов
            #print(actual_num_types , num_champions,num_childs,ibottype, ibottype // num_childs, ibottype // num_champions )
            i_champ_type = ibottype // num_childs
            bot_types[ibottype].N.W = champs[i_champ_type][1].W.copy()
            bot_types[ibottype].N.B = champs[i_champ_type][1].B.copy()
            bot_types[ibottype].N.Wi = champs[i_champ_type][1].Wi.copy()
            bot_types[ibottype].N.Bi = champs[i_champ_type][1].Bi.copy()
            bot_types[ibottype].N.Wo = champs[i_champ_type][1].Wo.copy()
            bot_types[ibottype].N.Bo = champs[i_champ_type][1].Bo.copy()

            bot_types[ibottype].N.mutate()
            connectomes.append(bot_types[ibottype].N)

    print("actual_num_types: {0:d}".format(actual_num_types))
    champs=[]
    for ibottype in range(actual_num_types):
        score = 0
        for i_try in range(num_tries):  # количество испытаний одного бота
            field1 = field()
            X, Y, Ins, Outs, Info = round(bot_types[ibottype], field1, num_bots, num_steps, dt)
            score += field1.score
            # print("ibottype: ", ibottype, " i_try: ", i_try, " score: ", field1.score)
        meanScore = score / num_tries
        meanScores.append(meanScore)
        champs.append((bot_types[ibottype], bot_types[ibottype].N, meanScore ) )
        # print("ibottype: ", ibottype, " meanScore: ", meanScore )
        Entry=[  ]
        Entry.extend(bot_types[ibottype].N.W.flat)
        Entry.extend(bot_types[ibottype].N.B.flat)
        Entry.extend(bot_types[ibottype].N.Wi.flat)
        Entry.extend(bot_types[ibottype].N.Bi.flat)
        Entry.extend(bot_types[ibottype].N.Wo.flat)
        Entry.extend(bot_types[ibottype].N.Bo.flat)
        Entry.append(j)
        Entry.append(meanScore)
        #now = datetime.datetime.now()
        #print(now.strftime("%d-%m-%Y %H:%M"), "ibottype: {1:d}; meanScore: {0:.3f}".format(meanScore, ibottype))
        # rows.append(Entry)
        with open(OUTPUT_FILENAME, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerows([Entry])
    champs=sorted(champs, key= lambda x: x[2], reverse=True )

    if FIRST_GEN_GET_FROM!=1 or j!=0:
        champs=champs[0:num_champions]

    BotTypeHystory.append(bot_types)
    ConnectomesHistory.append(connectomes)
    genMeanScore = np.mean(meanScores)
    genChampMeanScore = np.mean([ champ[2] for champ in  champs])
    genMeanScores.append(genMeanScore)

    now = datetime.datetime.now()
    print(now.strftime("%d-%m-%Y %H:%M"), "generation: {1:d}; genMeanScore: {0:.3f}, genChampMeanScore: {2:.3f}".format(genMeanScore, j, genChampMeanScore))
    # plt.matshow(champConnectomes[0].Wi)
    # plt.show()




#print(rows)


plt.plot(genMeanScores)
plt.show()
print("genMeanScores: {}".format(genMeanScores))
field1 = field()
X, Y, Ins, Outs, Info = round(BotTypeHystory[0][0], field1, num_bots, num_steps, dt)
print(Ins, Outs)
plot_round( [X, Y] , field1.X1, field1.X2, field1.R, Ins, Outs)

field1 = field()
X, Y, Ins, Outs, Info = round(BotTypeHystory[0][1], field1, num_bots, num_steps, dt)
plot_round( [X, Y] , field1.X1, field1.X2, field1.R, Ins, Outs)


for i in range(1, num_champions ):
    field1 = field()
    X, Y, Ins, Outs, Info = round(champs[i][0], field1, num_bots, num_steps, dt)

    plot_round( [X, Y] , field1.X1, field1.X2, field1.R, Ins, Outs)



        
