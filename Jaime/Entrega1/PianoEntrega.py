import numpy as np
import pyaudio, kbhit
from scipy.io import wavfile
""" Iniciar con 'c' (suena un do)
    'e' = bajar 1 semitono
    'w' = subir 1 semitono
    entre 'c' y '-' las teclas blancas
    entre 'f' y 'ñ' las teclas negras (en sus respectivas posiciones respecto a las teclas blancas)
    't' = activar/desactivar mas de un tono a la vez
    'r' = delay de un segundo de lo que este sonando
"""
SRATE, data = wavfile.read("piano.wav")
CHUNK = 1024
p = pyaudio.PyAudio()
numbloque = 0
bloque = np.arange(CHUNK, dtype = data.dtype)
kb = kbhit.KBHit()
c = ' '
cAux = ' '
multi=False
dataPlay = np.zeros(len(data),dtype=int)

if data.dtype.name =='int16':fmt = 2
elif data.dtype.name =='int32':   fmt = 4
elif data.dtype.name =='float32': fmt = 4
elif data.dtype.name =='uint8':   fmt = 1
else: raise Exception('Not supported')

stream = p.open(format = p.get_format_from_width(fmt),
                channels = len(data.shape),
                rate = SRATE,
                frames_per_buffer = CHUNK,
                output = True)
 #               stream_callback=callback)
def delay(data,nb,dur,CHUNK):
    dataTemp=[]
    dataTemp=np.append(dataTemp,data[:nb*CHUNK+CHUNK])
    dataTemp=np.append(dataTemp,np.zeros(dur*20*CHUNK,dtype=int))
    dataTemp=np.append(dataTemp,data[nb*CHUNK+CHUNK:])
    return dataTemp

def changeTone(tone,dattt):
    cont = 0
    dataPlay=np.zeros(len(dattt),dtype=int)
    for x in range(len(dattt)):
        if x % tone == 0:
            if(x!= 0):
                cont = cont + 1
        if (x+cont < len(dattt)):
            dataPlay[x] = dattt[x+cont]
    return dataPlay

def numTones(num,dataPlay):
    dat = dataPlay
    for i in range(num):
        dat = changeTone(17,dat)
    return dat
def changeToneDown(tone,dattt):
    cont = 0
    dataPlay=np.zeros(len(dattt)+(len(dattt)//tone),dtype=int)
    for x in range(len(dataPlay)):
        if x % tone == 0:
            if(x!= 0):
                dataPlay[x] = (dattt[x-cont] + dattt[x-cont-1])/2
                cont = cont + 1
        elif (x+cont < len(dattt)):
            dataPlay[x] = dattt[x-cont]
    return dataPlay
def merge(dataAux,da,currBloc):
    dataAux = dataAux[currBloc*CHUNK:]
    if (len(da) > len(dataAux)):
        da2 = da
        for x in range(len(dataAux)):
            da2[x] = (da[x] + dataAux[x]) / 2
    else:
        da2 = dataAux
        for x in range(len(da)):
            da2[x] = (da[x] + dataAux[x]) / 2
    return da2

while c != 'q':
    bloque = dataPlay[numbloque*CHUNK:numbloque*CHUNK+CHUNK]
    stream.write(bloque.astype((data.dtype)).tobytes())
    bloqueAux = numbloque
    dataAux = dataPlay
    if kb.kbhit():
        c = kb.getch()    
        if c == 'c':
            numbloque = 0
            dataPlay = data
            dataPlay = changeTone(17,dataPlay)
            dataPlay = changeToneDown(17,dataPlay)
        elif c == 'w':
            numbloque = 0
            dataPlay = changeTone(17,dataPlay)
        elif c == 'r':
            dataPlay = delay(dataPlay,numbloque,1,CHUNK)
        elif c == 'e':
            numbloque = 0
            dataPlay = changeToneDown(17,dataPlay)
        elif c == 'f':
            numbloque = 0
            dataPlay = numTones(1,data)
        elif c == 'v':
            numbloque = 0
            dataPlay = numTones(2,data)
        elif c == 'g':
            numbloque = 0
            dataPlay = numTones(3,data)
        elif c == 'b':
            numbloque = 0
            dataPlay = numTones(4,data)
        elif c == 'n':
            numbloque = 0
            dataPlay = numTones(5,data)
        elif c == 'j':
            numbloque = 0
            dataPlay = numTones(6,data)
        elif c == 'm':
            numbloque = 0
            dataPlay = numTones(7,data)
        elif c == 'k':
            numbloque = 0
            dataPlay = numTones(8,data)
        elif c == ',':
            numbloque = 0
            dataPlay = numTones(9,data)
        elif c == 'l':
            numbloque = 0
            dataPlay = numTones(10,data)
        elif c == '.':
            numbloque = 0
            dataPlay = numTones(11,data)
        elif c == 't':
            if multi == True:
                multi = False
            else:
                multi = True            
        if(len(bloque) != 0 and cAux != c and c != ' ' and multi == True):
            dataPlay = merge(dataAux,dataPlay,bloqueAux)
        cAux = c
    numbloque += 1

kb.set_normal_term()
stream.stop_stream()
stream.close()
p.terminate()