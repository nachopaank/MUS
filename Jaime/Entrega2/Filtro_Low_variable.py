import numpy as np
import pyaudio, kbhit
import os
from scipy.io import wavfile

SRATE, data = wavfile.read("tormenta.wav")
CHUNK = 1024
p = pyaudio.PyAudio()
clear = lambda: os.system('cls')
#numbloque = 0
bloque = np.arange(CHUNK, dtype = data.dtype)
kb = kbhit.KBHit()
c = ' '
#cAux = ' '
#multi=False
#dataPlay = np.zeros(len(data),dtype=int)
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


alpha = 1
prev = 0
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
            if 1 < alpha + 0.1:
                alpha = 1
            else:
                alpha+=0.1
            #frame = 0
        elif c == 'v':
            if 0 > alpha - 0.1:
                alpha = 0
            else:
                alpha-=0.1
           
            #frame = 0
        elif c == 'x':
            frame = 0
        clear()
        print("Alpha= ",alpha)
    if len(bloque) > 0:
        prev = bloque[len(bloque)-1]
        stream.write(bloque.astype((data.dtype)).tobytes())
        frame+=1
       

kb.set_normal_term()
stream.stop_stream()
stream.close()
p.terminate()