import numpy as np
import math
import numpy.random as rand
import matplotlib.pyplot as plt
from N_net_class import network
import pandas as pd

def sum_of_squares(v):
    """ v1 * v1 + v2 * v2 ... + vn * vn"""
    # или return dot_product(v, v)
    return sum(vi ** 2 for vi in v)

def magnitude(v):
    return math.sqrt(sum_of_squares(v))

class field(object):
    def __init__(self):
        self.R=0.1
        self.X1 = np.array([rand.random(), rand.random()])
        self.X2 = np.array([rand.random(), rand.random()])
        self.noisemakers = []
        self.score = 0

    def move(self, dt):
        # размер пятна постоянный
        R = self.R
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
        R = self.R
        if magnitude(Coor - self.X1) < R or magnitude(Coor - self.X2) < R:
            return 1
        else:
            return 0

class bot(object):
    def __init__(self, NN = [4, 6, 6, 5], V=np.array([0, 0]), X=0.25, Y=0.75, VL=0.0, VR=0.0, fi=np.array([1, 0]), mutType =1, mutRate=0.05):
        self.NN = NN
        self.V = V
        self.X = X
        self.Y = Y
        self.VL = VL
        self.VR = VR
        self.fi = fi
        # NL=1, Nn=6, Ni=4, No=3
        self.N = network(NN, seed=0, mutType=mutType, mutRate=mutRate)
        self.N_Out=list(range(self.NN[2]))


    def motion(self, VL, VR, dt):
        V = self.V
        fi = self.fi
        # print("V:", V)
        self.X += V[0] * dt
        self.Y += V[1] * dt
        # коэффициент преобразования момента на моторе в ускорение
        k_mot = 0.1
        # ширина колесной пары
        H = 0.5
        dfi = k_mot * (VR - VL) / H
        v1_new = (V[0] * np.cos(dfi)) - (V[1] * np.sin(dfi))
        v2_new = (V[1] * np.cos(dfi)) + (V[0] * np.sin(dfi))
        V = np.array([v1_new, v2_new])
        if magnitude(V) != 0:
            fi = V / magnitude(V)
        self.fi = fi
        dV = k_mot * (VL + VR) / 2
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
        In = [self.V[0], self.V[1], grtype, field.soundlevel(Coor, V), self.N_Out[3], self.N_Out[4]]
        # print(In)
        [VL, VR, sound, O1, O2] = self.N.go(In)
        Out = [VL, VR, sound, O1, O2]
        self.N_Out=Out.copy()
        self.VL=Out[0]
        self.VR = Out[1]
        field.placenoisemaker(self.X, self.Y, sound)
        # print("motors: ", VL,VR)
        self.motion(VL, VR, dt)
        return In, Out

def round(bottype, field1, num_bots, num_steps, dt):
    connectome = bottype.N
    X, Y, Ins, Outs, Info = [], [], [], [], []
    bots = []
    In, Out = [], []
    for ibot in range(num_bots):  # создание ботов-клонов
        Ins.append([])
        Outs.append([])
        Info.append([])
        (Xbot, Ybot) = rand.random((2))
        while field1.groundtype([Xbot,Ybot])==1:
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
    return X, Y, Ins, Outs, Info

def plot_round(XY,X1, X2, R, Ins, Outs):
    X,Y=XY
    ax = plt.gca()
    circle1 = plt.Circle((X1[0], X1[1]), R, color='r', fill=False)
    circle2 = plt.Circle((X2[0], X2[1]), R, color='r', fill=False)
    ax.add_patch(circle1)
    ax.add_patch(circle2)
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
                #fi = Info[ibot][i_step]
                #str8 = "fi" + "{0:.2f}, {1:.2f}".format(fi[0], fi[1]) + "\n"
                # str8 = "fi" + "{0}".format(Info[ibot][i_step]) + "\n"
                str = str3 + str4 + str7
                ax.annotate(str, (X[ibot][i_step], Y[ibot][i_step]))
    plt.show()

def numParams(file_NN):
    input_NL = file_NN[0]
    input_Nn = file_NN[1]
    input_Ni = file_NN[2]
    input_No = file_NN[3]
    W_start = 0
    W_end = W_start + input_Nn * input_Nn * input_NL
    B_start = W_end
    B_end = B_start + input_Nn * input_NL
    Wi_start = B_end
    Wi_end = Wi_start + input_Nn * input_Ni
    Bi_start = Wi_end
    Bi_end = Bi_start + input_Nn
    Wo_start = Bi_end
    Wo_end = Wo_start + input_Nn * input_No
    Bo_start = Wo_end
    Bo_end = Bo_start + input_No
    return W_start, W_end, B_start, B_end, Wi_start, Wi_end, Bi_start, Bi_end, Wo_start, Wo_end, Bo_start, Bo_end

def readChamps(inputfilename, file_NN):
    dt = pd.read_csv(inputfilename)
    input_NL = file_NN[0]
    input_Nn = file_NN[1]
    input_Ni = file_NN[2]
    input_No = file_NN[3]
    # NL=1, Nn=6, Ni=4, No=3
    inputdata = dt.to_numpy()
    inputdatashape = inputdata.shape
    #print(inputdatashape)
    W_start = 0
    W_end = W_start + input_Nn * input_Nn * input_NL
    B_start = W_end
    B_end = B_start + input_Nn * input_NL
    Wi_start = B_end
    Wi_end = Wi_start + input_Nn * input_Ni
    Bi_start = Wi_end
    Bi_end = Bi_start + input_Nn
    Wo_start = Bi_end
    Wo_end = Wo_start + input_Nn * input_No
    Bo_start = Wo_end
    Bo_end = Bo_start + input_No
    #print(W_start, W_end, B_start, B_end, Wi_start, Wi_end, Bi_start, Bi_end, Wo_start, Wo_end, Bo_start, Bo_end)
    inputConnectomes=[]
    for i_row in range(inputdatashape[0]):
        row = inputdata[i_row, :]
        W = np.reshape(row[W_start:W_end], (input_Nn, input_Nn, input_NL))

        B = np.reshape(row[B_start:B_end], (input_Nn, input_NL))

        Wi = np.reshape(row[Wi_start:Wi_end], (input_Ni, input_Nn))

        Bi = np.reshape(row[Bi_start:Bi_end], (input_Nn))

        Wo = np.reshape(row[Wo_start:Wo_end], (input_No, input_Nn))

        Bo = np.reshape(row[Bo_start:Bo_end], (input_No))
        N=network(file_NN, seed=0, mutType=1, mutRate=0.1)
        N.W = W.copy()
        N.B = B.copy()
        N.Wi = Wi.copy()
        N.Bi = Bi.copy()
        N.Wo = Wo.copy()
        N.Bo = Bo.copy()
        inputConnectomes.append(N)
    return (inputConnectomes)
