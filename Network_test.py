import maroccolib as mc
import csv

inputfilename="BestPoints_NL4_16gen.csv"
outputfilename="colours_NL4_16gen"
file_NN = [4, 6, 6, 5]
inputConnectomes = mc.readChamps(inputfilename, file_NN)
#connectome=inputConnectomes[0]

colormapV={ '[-1. -1.]': 0.,
            '[-1. 1.]': 0.25,
            '[-1.  1.]': 0.25,
            '[1. -1.]': 0.5,
            '[ 1. -1.]': 0.5,
            '[1. 1.]': 0.75,
           }
No=0
for connectome in inputConnectomes:
    for grtype in range(-1,2):
        for SL in [-1 + c * 0.2 for c in range(11)]:
            for V0i in [-1 + c * 0.2 for c in range(11)]:
                Outs=[]
                for V1i in [-1 + c * 0.2 for c in range(11)]:
                    for Out1 in [-1 + c * 0.2 for c in range(11)]:
                        for Out2 in [-1 + c * 0.2 for c in range(11)]:
                            In=[V0i, V1i, grtype, SL, Out1, Out2]
                            Out=connectome.go(In)
                            Outs.append(Out)
                            OutV=str(Out[0:2])
                            color_VLR=colormapV[OutV]
                            Entry=[]
                            Entry.extend(In)
                            Entry.append(color_VLR)
                            Entry.extend(Out)
                            strNoFile='{0:d}'.format(No)
                            with open(outputfilename+strNoFile+'.csv', "a", newline="") as file:
                                writer = csv.writer(file)
                                writer.writerows([Entry])
    print('done: '+strNoFile )
    No+=1
            #print(','.join(Outs))
#In = [self.V[0], self.V[1], grtype, field.soundlevel(Coor, V)]
# print(In)
#[VL, VR, sound] = self.N.go(In)