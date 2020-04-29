import numpy as np
import pyaudio, kbhit
from scipy.io import wavfile
import os


SRATE, data = wavfile.read("tormenta.wav")
CHUNK = 1024
p = pyaudio.PyAudio()
#numbloque = 0
bloque = np.arange(CHUNK, dtype = data.dtype)
kb = kbhit.KBHit()
c = ' '
clear = lambda: os.system('cls')
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
 #               stream_callback=callback)


alpha = 0.5
prev = 0
flag = True
print("Alpha= ",alpha)
while c!= 'q':
    bloqueAux = data[frame*CHUNK:(frame+1)*CHUNK]
    bloque = np.copy(bloqueAux)

    bloque.setflags(write=1) # para poder escribir

    if len(bloque) > 0:
        bloque[0] = prev + alpha * (bloque[0]-prev)
        for i in range(1,len(bloque)):
            bloque[i] = bloque[i-1] + alpha * (bloque[i]-bloque[i-1])

    if kb.kbhit():
        c = kb.getch()    
        if c == 'c':
            if 1 < alpha * 2:
                alpha = 1
            else:
                alpha*=2
            #frame = 0
        elif c == 'x':
            if 0 > alpha / 2:
                alpha = 0
            else:
                alpha/=2
           
            #frame = 0
        elif c == 'r':
            frame = 0
        elif c == 'a':
            if flag:
                flag = False   # High-Pass
            else:
                flag = True    # Low-Pass
        clear()
        print("Alpha= ",alpha)

    if len(bloque) > 0:
        prev = bloque[len(bloque)-1]
        bloqueHigh = np.copy(bloqueAux)
        bloqueHigh = np.subtract(bloqueHigh,bloque)
        
        if flag:
            stream.write(bloqueHigh.astype((data.dtype)).tobytes())
        else:
            stream.write(bloque.astype((data.dtype)).tobytes())
        frame+=1

kb.set_normal_term()
stream.stop_stream()
stream.close()
p.terminate()