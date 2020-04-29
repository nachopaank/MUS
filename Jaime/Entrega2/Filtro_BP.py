import numpy as np
import pyaudio, kbhit
from scipy.io import wavfile
import os
clear = lambda: os.system('cls')
SRATE, data = wavfile.read("tormenta.wav")
CHUNK = 1024
p = pyaudio.PyAudio()
bloque = np.arange(CHUNK, dtype = data.dtype)
kb = kbhit.KBHit()
c = ' '
frame = 0

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

low = 0.4
high = 0.6
prev = 0
flag = False

"""alpha = 0.5
prev = 0
flag = True"""#Cambiar alpha y su bloque para tener la suma de los 2 filtros
#Conseguir cambiar la posicion del ancho de banda
#Conseguir cambiar el ancho de banda

while c!= 'q':
    bloqueAux = data[frame*CHUNK:(frame+1)*CHUNK]
    bloqueLow = np.copy(bloqueAux)
    bloqueHigh = np.copy(bloqueAux)

    bloqueLow.setflags(write=1) # para poder escribir
    bloqueHigh.setflags(write=1)

    #Construccion del paso bajo
    if len(bloqueLow) > 0:
        bloqueLow[0] = prev + low * (bloqueLow[0]-prev)
        for i in range(1,len(bloqueLow)):
            bloqueLow[i] = bloqueLow[i-1] + low * (bloqueLow[i]-bloqueLow[i-1])

    #Construccion del paso alto
    if len(bloqueHigh) > 0:
        bloqueHigh[0] = prev + high * (bloqueHigh[0]-prev)
        for i in range(1,len(bloqueHigh)):
            bloqueHigh[i] = bloqueHigh[i-1] + high * (bloqueHigh[i]-bloqueHigh[i-1])
        #Contruccion del bloque final
        bloqueFin = np.subtract(bloqueHigh,bloqueLow)

    if kb.kbhit():
        c = kb.getch()   
        #Desplazar banda a la derecha 
        if c == 'c':
            if high + 0.1 <= 1:
                high += 0.1
                low += 0.1
        #Desplazar banda a la izquierda
        elif c == 'x':
            if low - 0.1 >= 0:
                low -= 0.1
                high -= 0.1

        #Desplazar independientemente
        elif c == 's':
            if low - 0.1 >= 0:
                low -= 0.1
        elif c == 'd':
            if low + 0.1 <= high:
                low += 0.1
        elif c == 'w':
            if high - 0.1 >= low:
                high -= 0.1
        elif c == 'e':
            if high + 0.1 <= 1:
                high += 0.1
        #Inversion de Filtro
        elif c == 'a':
            if flag:
                flag = False
            else:
                flag = True
            
            #Reset
        elif c == 'r':
            frame = 0
        clear()
        print("Low= ",low," High= ", high)

    if len(bloqueLow) > 0:
        if flag:
            bloqueFin = np.subtract(bloqueAux,bloqueFin)
        stream.write(bloqueFin.astype((data.dtype)).tobytes())
        frame+=1
        

kb.set_normal_term()
stream.stop_stream()
stream.close()
p.terminate()