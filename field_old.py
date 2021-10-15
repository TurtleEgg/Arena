import numpy as np
import math
import numpy.random as rand
from N_net_class import Network


def sum_of_squares(v):
    """ v1 * v1 + v2 * v2 ... + vn * vn"""
    # или return dot_product(v, v)
    return sum(vi ** 2 for vi in v)


def magnitude(v):
    return math.sqrt(sum_of_squares(v))


class Field(object):
    def __init__(self):
        self.X1 = np.array([0.25, 0.75])
        self.X2 = np.array([0.75, 0.25])
        self.noisemakers = []
        self.score = 0

    def move(self, dt):
        # размер пятна постоянный
        R = 0.2
        sc_sing = 1
        sc_bi = 2
        sc_tri = -1
        sc_quat = -2
        addscore = 0
        S1 = []
        S2 = []
        for Xi, Yi, leveli in self.noisemakers:
            S1.append(magnitude([Xi, Yi] - self.X1))
            S2.append(magnitude([Xi, Yi] - self.X2))
        count1 = 0
        count2 = 0
        for s in S1:
            if s < R:
                count1 += 1
        for s in S2:
            if s < R:
                count2 += 1

        if count1 == 1:
            addscore += sc_sing * dt
        elif count1 == 2:
            addscore += sc_bi * dt
        elif count1 == 3:
            addscore += sc_tri * dt
        elif count1 == 4:
            addscore += sc_quat * dt
        if count2 == 1:
            addscore += sc_sing * dt
        elif count2 == 2:
            addscore += sc_bi * dt
        elif count2 == 3:
            addscore += sc_tri * dt
        elif count2 == 4:
            addscore += sc_quat * dt
        self.score += addscore

        self.noisemakers = []

    def placenoisemaker(self, X, Y, level):
        self.noisemakers.append((X, Y, level))
        # print("noisemaker placed: ",X,Y,level )

    def soundlevel(self, Coor, V):
        X = Coor[0]
        Y = Coor[1]
        Vx = V[0]
        Vy = V[1]
        level = 0
        # когда смотришь прямо на звук, коэффициент сигнала1, когда спиной - 0
        for Xi, Yi, leveli in self.noisemakers:
            S = magnitude([X - Xi, Y - Yi])
            if S != 0:
                # единичный вектор направления от источника к слушателю
                n = np.array([(X - Xi) / S, (Y - Yi) / S])
                li = np.dot([Vx, Vy], n)
                if li > 0:
                    level = +li
        return level

    def groundtype(self, Coor=[0.25, 0.75]):
        Coor = np.array(Coor)

        # размер пятна постоянный
        R = 0.2
        if magnitude(Coor - self.X1) < R or magnitude(Coor - self.X2) < R:
            return 1
        else:
            return 0


class bot(object):
    def __init__(self, V=np.array([0, 0]), X=0.25, Y=0.75, VL=0.0, VR=1, fi=np.array([1, 0])):
        self.V = V
        self.X = X
        self.Y = Y
        self.VL = VL
        self.VR = VR
        self.fi = fi
        NN = [1, 2, 4, 3]  # NL=1, Nn=6, Ni=4, No=3
        self.N = Network(NN, seed=0, mutType=1, mutRate=0.1)

    def motion(self, VL, VR, dt):
        V = self.V
        fi = self.fi
        # print("V:", V)
        self.X += V[0] * dt
        self.Y += V[1] * dt
        # коэффициент преобразования момента на моторе в ускорение
        k_rot = 0.1
        # ширина колесной пары
        H = 1
        dfi = k_rot * (VR - VL) / H
        v1_new = (V[0] * np.cos(dfi)) - (V[1] * np.sin(dfi))
        v2_new = (V[1] * np.cos(dfi)) + (V[0] * np.sin(dfi))
        V = np.array([v1_new, v2_new])
        if magnitude(V) != 0:
            fi = V / magnitude(V)
        self.fi = fi
        dV = k_rot * (VL + VR) / 2
        V = dV * fi + V
        if self.X > 1:
            self.X = 1
            V[0] = -V[0]
        elif self.X < 0:
            self.X = 0
            V[0] = -V[0]
        if self.Y > 1:
            self.Y = 1
            V[1] = -V[1]
        elif self.Y < 0:
            self.Y = 0
            V[1] = -V[1]
        self.V = V

    def move(self, field, dt):
        # промежуток времени - постоянный
        Coor = [self.X, self.Y]
        grtype = field.groundtype(Coor)
        # print("groundtype: ", grtype)
        V = self.V
        In = [self.V[0], self.V[1], grtype, field.soundlevel(Coor, V)]
        # print(In)
        [VL, VR, sound] = self.N.go(In)
        Out = [VL, VR, sound]
        field.placenoisemaker(self.X, self.Y, sound)
        # print("motors: ", VL,VR)
        self.motion(VL, VR, dt)
        return In, Out


import matplotlib.pyplot as plt


def round(bottype, field, num_bots, num_steps, dt):
    connectome = bottype.N
    X, Y, Ins, Outs, Info = [], [], [], [], []
    bots = []
    In, Out = [], []
    for ibot in range(num_bots):  # создание ботов-клонов
        Ins.append([])
        Outs.append([])
        Info.append([])
        (Xbot, Ybot) = rand.random((2))
        V = np.array([-1+2*rand.random(), -1+2*rand.random()])
        bots.append(bot(V=V, X=Xbot, Y=Ybot))
        bots[ibot].N.W = connectome.W.copy()
        bots[ibot].N.B = connectome.B.copy()
        bots[ibot].N.Wi = connectome.Wi.copy()
        bots[ibot].N.Bi = connectome.Bi.copy()
        bots[ibot].N.Wo = connectome.Wo.copy()
        bots[ibot].N.Bo = connectome.Bo.copy()
        X.append([Xbot])
        Y.append([Ybot])

    for i_step in range(num_steps):  # испытание клонов
        field1.move(dt)

        for ibot in range(num_bots):
            In_i, Out_i = bots[ibot].move(field1, dt)
            Ins[ibot].append(In_i)
            Outs[ibot].append(Out_i)
            Info[ibot].append(bots[ibot].fi)
            # print("V: ", bot1.V)
            # print("Vmagn: ", magnitude(bots[ibot].V))
            X[ibot].append(bots[ibot].X)
            Y[ibot].append(bots[ibot].Y)
            # plt.scatter(bot1.X, bot1.Y)
            # ax.plot(X[ibot], Y[ibot])
    return X, Y, FieldX, FieldY, Ins, Outs, Info


def plot_round(X, Y, Ins, Outs):
    ax = plt.gca()
    #circle1 = plt.Circle((0.25, 0.75), 0.2, color='r', fill=False)
    #circle2 = plt.Circle((0.75, 0.25), 0.2, color='r', fill=False)
    #ax.add_patch(circle1)
    #ax.add_patch(circle2)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    num_bots = len(X)
    str = ''
    for ibot in range(num_bots):
        plt.scatter(X[ibot][0], Y[ibot][0])
        ax.plot(X[ibot], Y[ibot])
        for i_step in range(len(X[0]) - 1):
            if (i_step + 1) % 20 == 0:
                str1 = "VX" + "{0:.2f}".format(Ins[ibot][i_step][0]) + "\n"
                str2 = "VY" + "{0:.2f}".format(Ins[ibot][i_step][1]) + "\n"
                str3 = "gr" + "{0:.2f}".format(Ins[ibot][i_step][2]) + "\n"
                str4 = "sl" + "{0:.2f}".format(Ins[ibot][i_step][3]) + "\n"
                str5 = "VL" + "{0:.2f}".format(Outs[ibot][i_step][0]) + "\n"
                str6 = "VR" + "{0:.2f}".format(Outs[ibot][i_step][1]) + "\n"
                str7 = "S" + "{0:.2f}".format(Outs[ibot][i_step][2]) + "\n"
                fi = Info[ibot][i_step]
                str8 = "fi" + "{0:.2f}, {1:.2f}".format(fi[0], fi[1]) + "\n"
                # str8 = "fi" + "{0}".format(Info[ibot][i_step]) + "\n"
                str = str4 + str7
                ax.annotate(str, (X[ibot][i_step], Y[ibot][i_step]))
    plt.show()


num_steps = 100
dt = 1 / num_steps
num_bots = 4
rand.seed()
num_genotypes_in_step = 1000
num_tries = 20  # количество испытаний одного бота - испытано в test_mean для num_steps = 100
num_gens = 2  # количество поколений
champ_threshold = 1.0

genMeanScores = []
ConnectomesHistory = []
BotTypeHystory = []
for j in range(num_gens):

    bots = []

    # инициализация ботов
    bot_types = []
    connectomes = []
    meanScores = []
    for ibottype in range(num_genotypes_in_step):  # посев одного поколения ботов

        if j == 0:  # в первом поколении - генерируем
            bot_types.append(bot())
            connectomes.append(bot_types[ibottype].N)
        else:  # в последующих поколениях - мутируем чемпионов
            bot_types.append(bot())
            if ibottype < num_mutations * num_champs:
                i_champ_type = ibottype // num_mutations

                bot_types[ibottype].N.W = champConnectomes[i_champ_type].W.copy()
                bot_types[ibottype].N.B = champConnectomes[i_champ_type].B.copy()
                bot_types[ibottype].N.Wi = champConnectomes[i_champ_type].Wi.copy()
                bot_types[ibottype].N.Bi = champConnectomes[i_champ_type].Bi.copy()
                bot_types[ibottype].N.Wo = champConnectomes[i_champ_type].Wo.copy()
                bot_types[ibottype].N.Bo = champConnectomes[i_champ_type].Bo.copy()
            else:
                i_champ_type = num_champs - 1

                bot_types[ibottype].N.W = champConnectomes[i_champ_type].W.copy()
                bot_types[ibottype].N.B = champConnectomes[i_champ_type].B.copy()
                bot_types[ibottype].N.Wi = champConnectomes[i_champ_type].Wi.copy()
                bot_types[ibottype].N.Bi = champConnectomes[i_champ_type].Bi.copy()
                bot_types[ibottype].N.Wo = champConnectomes[i_champ_type].Wo.copy()
                bot_types[ibottype].N.Bo = champConnectomes[i_champ_type].Bo.copy()
            # print("ibottype, i_champ_type: ", ibottype, i_champ_type)
            # print("champConnectomes[i_champ_type].Wi", champConnectomes[i_champ_type].Wi)
            # print("bot_types[ibottype].N.Wi", bot_types[ibottype].N.Wi)
            # print(bot_types[ibottype].N)
            bot_types[ibottype].N.mutate()
            # print("mutate!")
            # print(bot_types[ibottype].N)
            # print("champConnectomes[i_champ_type].Wi", champConnectomes[i_champ_type].Wi)
            # print("bot_types[ibottype].N.Wi", bot_types[ibottype].N.Wi)

        connectomes.append(bot_types[ibottype].N)
        score = 0

        for i_try in range(num_tries):  # количество испытаний одного бота
            field1 = field()
            X, Y, Ins, Outs, Info = round(bot_types[ibottype], field1, num_bots, num_steps, dt)
            score += field1.score
            # print("ibottype: ", ibottype, " i_try: ", i_try, " score: ", field1.score)
        meanScore = score / num_tries
        meanScores.append(meanScore)
        # print("ibottype: ", ibottype, " meanScore: ", meanScore )
    BotTypeHystory.append(bot_types)
    ConnectomesHistory.append(connectomes)
    genMeanScore = np.mean(meanScores)
    genMeanScores.append(genMeanScore)
    champTypes = []
    champConnectomes = []
    champScores = []
    for ibottype in range(num_genotypes_in_step):  # define champions
        if meanScores[ibottype] >= champ_threshold * genMeanScore:
            champTypes.append(bot_types[ibottype])
            champConnectomes.append(connectomes[ibottype])
            champScores.append(meanScores[ibottype])
    print("generation: {1:d}; genMeanScore: {0:.3f}".format(genMeanScore, j))
    # plt.matshow(champConnectomes[0].Wi)
    # plt.show()
    num_champs = len(champTypes)
    num_mutations = num_genotypes_in_step // num_champs
plt.plot(genMeanScores)
plt.show()
print("genMeanScores: {}".format(genMeanScores))
field1 = field()
X, Y, Ins, Outs, Info = round(BotTypeHystory[0][0], field1, num_bots, num_steps, dt)
#print(Ins, Outs)
plot_round(X, Y, Ins, Outs)

field1 = field()
X, Y, Ins, Outs, Info = round(BotTypeHystory[0][1], field1, num_bots, num_steps, dt)
plot_round(X, Y, Ins, Outs)

for i in range(1, len(BotTypeHystory[num_gens - 1]), len(BotTypeHystory[num_gens - 1]) // 10  ):
    field1 = field()
    X, Y, Ins, Outs, Info = round(BotTypeHystory[num_gens - 1][i], field1, num_bots, num_steps, dt)
    plot_round(X, Y, Ins, Outs)

