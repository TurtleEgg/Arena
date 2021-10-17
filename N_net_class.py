import numpy as np
import numpy.random as rand

from hyper_parameters import HyperParameters

class Network(object):
    def __init__(self, NN, seed=0, hyper_parameters=HyperParameters()):
        #NL количество слоев
        #Nn количество нейронов в слое
        #Ni количество входов
        #No количество выходов
        #mutRate предел случайного измененеия значения при мутации
        #mutType =1 - меняются все нейроны на случайную величину в интервале -mutRate..mutRate;
        #mutType =2 - меняется один нейрон
        #NN:
        # NL = 1, Nn = 2, Ni = 10, No = 4
        self.NL = NN[0]
        self.Nn = NN[1]
        self.Ni = NN[2]
        self.No = NN[3]
        NL = NN[0]
        Nn = NN[1]
        Ni = NN[2]
        No = NN[3]

        self.hyper_parameters = hyper_parameters
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
        self.B = -np.ones((Nn, NL)) + 2 * rand.random((Nn, NL))
        self.W = -np.ones((Nn, Nn, NL))+ 2 * rand.random((Nn, Nn, NL))
        self.Bi = -np.ones((Nn))+ 2 * rand.random((Nn))
        self.Wi = -np.ones((Ni, Nn))+ 2 * rand.random((Ni, Nn))
        self.Bo = -np.ones((No))+ 2 * rand.random((No))
        self.Wo = -np.ones((No, Nn))+ 2 * rand.random((No, Nn))

    def go(self, In):
        NL = self.NL
        Nn = self.Nn
        Ni = self.Ni
        No = self.No
        B= self.B
        W= self.W
        Bi=self.Bi
        Wi=self.Wi
        Bo=self.Bo
        Wo=self.Wo


        L = np.zeros((Nn, NL)) #возбуждения нейронов

        L[:, 0] = np.sign(np.dot(Wi[:, 0], In) + Bi)

        for iL in range(1, NL):
            L[:, iL] = np.sign(np.dot(W[:, :, iL], L[:, iL - 1]) + B[:, iL])

        Out = np.sign(np.dot(Wo, L[:, NL - 1]) + Bo)
        print(f"Out: {Out}")
        self.L=L
        return Out

    def mutate(self):
        rand.seed()
        rate=self.hyper_parameters.mut_rate #максимально возможное изменение веса
        mutType = self.hyper_parameters.mut_type
        NL = self.NL
        Nn = self.Nn
        Ni = self.Ni
        No = self.No
        B = self.B
        W = self.W
        Bi = self.Bi
        Wi = self.Wi
        Bo = self.Bo
        Wo = self.Wo


        def randUpdate(Mat, rate, dims):
            # dims=dimensions длины сторон матрицы (iterable of integers)

            dims=list(dims)
            #print('измерения: ', dims)
            #print('элемент матрицы:', Mat)
            dim = dims.pop(0)
            for i in range(dim):
                if len(dims)==0:
                    delta=(-1+ 2 * rand.random(1) )
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
            self.B = randUpdate(B, rate, (Nn, NL))
            self.W = randUpdate(W, rate, (Nn, Nn, NL))
            self.Bi = randUpdate(Bi, rate, (Nn,)) #запятая висит потому что нужно сделать из integer - iterable object (список или кортеж)
            self.Wi = randUpdate(Wi, rate, (Ni, Nn))
            self.Bo = randUpdate(Bo, rate, (No,)) #запятая висит потому что нужно сделать из integer - iterable object (список или кортеж)
            self.Wo = randUpdate(Wo, rate, (No, Nn))



        elif mutType==2:
            # меняется один случайный вес, максимум на величину rate

            # подсчитываем количество элементов
            Bnp = np.array(B)
            numB = np.prod(Bnp.shape)
            Wnp=np.array(W)
            numW=np.prod(Wnp.shape)
            Binp = np.array(Bi)
            numBi = np.prod(Binp.shape)
            Winp = np.array(Wi)
            numWi = np.prod(Winp.shape)
            Bonp = np.array(Bo)
            numBo = np.prod(Bonp.shape)
            Wonp = np.array(Wo)
            numWo = np.prod(Wonp.shape)
            numN = [numB, numW, numBi, numWi, numBo, numWo]


            # выбираем какую матрицу обновлять пропорционально количеству элементов в них
            choice=rand.randint(0,np.sum(numN))
            if choice<numN[0]:
                self.B = randSingleUpdate(B, rate, (Nn, NL))
            if choice<sum(numN[0:1]):
                self.W = randSingleUpdate(W, rate, (Nn, Nn, NL))
            if choice<sum(numN[0:2]):
                self.Bi = randSingleUpdate(Bi, rate, (Nn,))
            if choice<sum(numN[0:3]):
                self.Wi = randSingleUpdate(Wi, rate, (Ni, Nn))
            if choice<sum(numN[0:4]):
                self.Bo = randSingleUpdate(Bo, rate, (No,))
            if choice<sum(numN[0:5]):
                self.Wo = randSingleUpdate(Wo, rate, (No, Nn))

        else:
            return 1
        return 0

# Test

