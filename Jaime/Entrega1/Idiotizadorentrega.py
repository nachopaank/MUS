# basic/record0.py Grabacion de un archivo de audio 'q' para terminar
import pyaudio, wave, kbhit
import numpy as np
CHUNK = 1024; FORMAT = pyaudio.paInt16; CHANNELS = 2; RATE = 44100
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS,
    rate=RATE, input=True, # ahora es flujo de entrada
    frames_per_buffer=CHUNK) # tamanio buffer == CHUNK !!
stream2 = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                frames_per_buffer = CHUNK,
                output = True)
frames = [] # lista de samples
kb = kbhit.KBHit()
c = ' '
data = stream.read(CHUNK)
def delay(data,nb,dur,CHUNK):
    dataTemp=[]
    dataTemp=np.append(dataTemp,data[:nb*CHUNK+CHUNK])
    dataTemp=np.append(dataTemp,np.zeros(dur*20*CHUNK,dtype=int))
    dataTemp=np.append(dataTemp,data[nb*CHUNK+CHUNK:])
    return dataTemp
while c != 'q': # grabando

    data = stream.read(CHUNK)
    #data = delay(data,0,1,CHUNK)
    stream2.write(data)
    if kb.kbhit(): 
        c = kb.getch()

kb.set_normal_term(); stream.stop_stream(); stream.close(); p.terminate()
#guardamos wav
