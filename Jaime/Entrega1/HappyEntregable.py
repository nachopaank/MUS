import numpy as np 
import pyaudio, wave, kbhit

CHUNK = 1024
SRATE = 44100
frame = 0

kb = kbhit.KBHit()
p = pyaudio.PyAudio()
data = []
vol = 1.0
c = ' '
numBloque = 0

# Escribo la cancion Happy Birthday de forma que sea facilmente leible
happy = [('G',0.5),('G',0.5),('A',1),('G',1),('c',1),('B',2),
('G',0.5),('G',0.5),('A',1),('G',1),('d',1),('c',2),
('G',0.5),('G',0.5),('g',1),('e',1),('c',1),('B',1),('A',1),
('f',0.5),('f',0.5),('e',1),('c',1),('d',1),('c',2)]

FORMAT = pyaudio.paFloat32; CHANNELS = 1
stream = p.open(format=FORMAT, channels=CHANNELS,
rate=SRATE, output=True,
frames_per_buffer=CHUNK) 


#Genero un oscilador con todos los parametros necesarios
def oscC2(frec, frame, vol, dur):
    data = vol*np.sin(2*np.pi*frec*(np.arange(CHUNK*dur)+frame*CHUNK)/SRATE)
    frame += CHUNK
    return data

# Me defino una funcion switch que no existe en python
def switch(nota):
    if nota == 'A':
        return 880
    elif nota == 'B':
        return 987.767 
    elif nota == 'C':
        return 523.251
    elif nota == 'D':
        return 587.33
    elif nota == 'E':
        return 659.255
    elif nota == 'F':
        return 698.456
    elif nota == 'G':
        return 783.991
    elif nota == 'a':
        return 880*2
    elif nota == 'b':
        return 987.767*2
    elif nota == 'c':
        return 523.251*2
    elif nota == 'd':
        return 587.33*2
    elif nota == 'e':
        return 659.255*2
    elif nota == 'f':
        return 698.456*2
    elif nota == 'g':
        return 783.991*2
    else:
        return 0

# Construtyo el data con las notas de Happy y le intercalo silencios 
# para que las notas consecutivas iguales suenen bien
for x in happy:
        data2 = oscC2(switch(x[0]), frame, vol, x[1]*20)
        data = np.append(data,data2)
        data = np.append(data, oscC2(0, frame, vol, 1))

# Y las reproduzco por bloques
while c != 'q':
    bloque = data[numBloque*CHUNK : numBloque*CHUNK+CHUNK]
    stream.write(bloque.astype((data.dtype)).tobytes())
    if kb.kbhit(): c = kb.getch()
    numBloque += 1
    
kb.set_normal_term()
stream.stop_stream()
stream.close()
kb.set_normal_term()
p.terminate()