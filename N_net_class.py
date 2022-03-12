from typing import Any, Dict, Tuple

import numpy as np
import numpy.random as rand

class Network(object):
    def __init__(self, NN, seed=0):
        #NL количество слоев
        #Nn количество нейронов в слое
        #Ni количество входов
        #No количество выходов
        #mutRate предел случайного измененеия значения при мутации
        #mutType =1 - меняются все нейроны на случайную величину в интервале -mutRate..mutRate;
        #mutType =2 - меняется один нейрон
        #NN:
        # NL = 1, Nn = 2, Ni = 10, No = 4

        self.NL = NN["layers"]
        self.Nn = NN["inner neurons"]
        self.Ni = NN["input neurons"]
        self.No = NN["output neurons"]

        self.dims = {"B": (self.Nn, self.NL),
                     "W": (self.Nn, self.Nn, self.NL),
                     "Bi": (self.Nn,),
                     "Wi": (self.Ni, self.Nn),
                     "Bo": (self.No,),
                     "Wo": (self.No, self.Nn)}

        if seed==0:
            rand.seed()
            #seedo=rand.randint(0, 2 ** 16)
            #self.seed = seedo
            #print(seedo)
            #rand.seed(self.seed)
        else:
            rand.seed(seed)
        #print(rand.random())
        # W - матрицы весов
        # B - векторы порогов
        # Инициализируются случайные значения в диапазоне -1..1
        self.B = -np.ones(self.dims["B"]) + 2 * rand.random(self.dims["B"])
        self.W = -np.ones(self.dims["W"]) + 2 * rand.random(self.dims["W"])
        self.Bi = -np.ones((self.Nn)) + 2 * rand.random((self.Nn))
        self.Wi = -np.ones((self.Ni, self.Nn)) + 2 * rand.random((self.Ni, self.Nn))
        self.Bo = -np.ones((self.No)) + 2 * rand.random((self.No))
        self.Wo = -np.ones((self.No, self.Nn)) + 2 * rand.random((self.No, self.Nn))

    def go(self, In):
        L = np.zeros((self.Nn, self.NL))  # возбуждения нейронов
        L[:, 0] = np.sign(np.dot(self.Wi[:, 0], In) + self.Bi)

        for iL in range(1, self.NL):
            L[:, iL] = np.sign(np.dot(self.W[:, :, iL], L[:, iL - 1]) + self.B[:, iL])

        # Out = np.sign(np.dot(Wo, L[:, NL - 1]) + Bo)
        Out = np.dot(self.Wo, L[:, self.NL - 1]) + self.Bo
        # print(f"Out: {Out}")
        self.L = L

        return Out

    def mutate(self, hyper_parameters: Dict[str, Any] = {"mut_rate": 0.05, "mut_type": 1}):
        rand.seed()
        rate = hyper_parameters["mut_rate"]  # максимально возможное изменение веса
        mutType = hyper_parameters["mut_type"]

        def randUpdate(Mat, rate, dims):
            # dims=dimensions длины сторон матрицы (iterable of integers)

            dims=list(dims)
            #print('измерения: ', dims)
            #print('элемент матрицы:', Mat)
            dim = dims.pop(0)
            for i in range(dim):
                if len(dims)==0:
                    #delta=(-1+ 2 * rand.random(1) )
                    delta = rand.normal(0, 0.5)
                    #print(delta)
                    Mat[i] += rate * delta
                    Mat[i]=float(Mat[i]) #костыль чтобы не вылезали array()
                    if Mat[i] < -1:
                        Mat[i] = -1
                    elif Mat[i] > 1:
                        Mat[i] = 1
                    #print('элемент матрицы:', Mat[i])
                else:
                    Mat[i]=randUpdate(Mat[i], rate, dims)
            return Mat

        def randSingleUpdate(Mat, rate, dims):
            # dims=dimensions длины сторон матрицы (iterable of integers)
            dims = list(dims)
            # print('измерения: ', dims)
            # print('элемент матрицы:', Mat)
            dim = dims.pop(0)
            i=rand.randint(0,dim)
            if len(dims) == 0:
                Mat[i] += rate * (-1 + 2 * rand.random(1))
                Mat[i] = float(Mat[i])  # костыль чтобы не вылезали array()
                if Mat[i] < -1:
                    Mat[i] = -1
                elif Mat[i] > 1:
                    Mat[i] = 1
                # print('элемент матрицы:', Mat[i])
            else:
                Mat[i] = randSingleUpdate(Mat[i], rate, dims)
            return Mat

        if mutType==1:
            # все веса и пороги меняются случайным образом, максимум на величину Rate
            self.B = randUpdate(self.B, rate, (self.Nn, self.NL))
            self.W = randUpdate(self.W, rate, (self.Nn, self.Nn, self.NL))
            self.Bi = randUpdate(self.Bi, rate, (
            self.Nn,))  # запятая висит потому что нужно сделать из integer - iterable object (список или кортеж)
            self.Wi = randUpdate(self.Wi, rate, (self.Ni, self.Nn))
            self.Bo = randUpdate(self.Bo, rate, (
            self.No,))  # запятая висит потому что нужно сделать из integer - iterable object (список или кортеж)
            self.Wo = randUpdate(self.Wo, rate, (self.No, self.Nn))

        elif mutType==2:
            # меняется один случайный вес, максимум на величину rate

            # подсчитываем количество элементов
            Bnp = np.array(self.B)
            numB = np.prod(Bnp.shape)
            Wnp = np.array(self.W)
            numW = np.prod(Wnp.shape)
            Binp = np.array(self.Bi)
            numBi = np.prod(Binp.shape)
            Winp = np.array(self.Wi)
            numWi = np.prod(Winp.shape)
            Bonp = np.array(self.Bo)
            numBo = np.prod(Bonp.shape)
            Wonp = np.array(self.Wo)
            numWo = np.prod(Wonp.shape)
            numN = [numB, numW, numBi, numWi, numBo, numWo]

            # выбираем какую матрицу обновлять пропорционально количеству элементов в них
            choice=rand.randint(0,np.sum(numN))
            if choice < numN[0]:
                self.B = randSingleUpdate(self.B, rate, (self.Nn, self.NL))
            if choice < sum(numN[0:1]):
                self.W = randSingleUpdate(self.W, rate, (self.Nn, self.Nn, self.NL))
            if choice < sum(numN[0:2]):
                self.Bi = randSingleUpdate(self.Bi, rate, (self.Nn,))
            if choice < sum(numN[0:3]):
                self.Wi = randSingleUpdate(self.Wi, rate, (self.Ni, self.Nn))
            if choice < sum(numN[0:4]):
                self.Bo = randSingleUpdate(self.Bo, rate, (self.No,))
            if choice < sum(numN[0:5]):
                self.Wo = randSingleUpdate(self.Wo, rate, (self.No, self.Nn))

        else:
            raise ValueError("incorrect mut_type")

# Test

