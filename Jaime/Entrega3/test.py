import numpy as np # arrays
import pyaudio, kbhit
import pygame
from pygame.locals import *

RATE = 44100; CHUNK = 1024

WIDTH = 64
HEIGHT = 480

# frecuencia dada f_k, frame inicial, volumen
def osc(frec,vol,frame):
    return vol*np.sin(2*np.pi*(np.arange(CHUNK)+frame)*frec/RATE) 

# fc carrier (pitch), fm frecuencia moduladora, beta = indice de modulacion
def oscFM(fc,fm,beta,vol,frame):
    # sin(2*pi*fc + beta * sin(2*pi*fm))
    interval = np.arange(CHUNK)+frame # array para el chunk
    mod = (RATE*beta)*np.sin(2*np.pi*fm*interval/RATE) # moduladora
    res = np.sin((2*np.pi*fc*interval+mod)/RATE) # portadora
    return vol*res

def timeToFrame(t): return int(t*RATE) # conversion tiempo a frame

def env(lst):
    last = timeToFrame(lst[len(lst)-1][0])
    last = last + CHUNK
    samples = np.zeros(last, dtype=np.float32) # senial con ceros
    for i in range(1,len(lst)):
        f1, f2 = timeToFrame(lst[i-1][0]), timeToFrame(lst[i][0])
        v1, v2 = lst[i-1][1], lst[i][1]
        for j in range(f1,f2): # formula de interpolacion
            samples[j] = v1 + (j-f1) * (v2-v1)/(f2-f1)

    return samples


fc = 300.0
fm = 1.0
beta = 1.0

vol = 0.0

maxFrec = 1000.0
maxVol = 1.0

ptosEnv = [(0.0,1.0),(100.0,1.0)]
last = len(ptosEnv)-1 # ultimo punto de la envolvente
endFrame = timeToFrame(ptosEnv[last][0]) # ultimo frame
print(ptosEnv[last][0])
envSamples = env(ptosEnv) # generamos samples envolvente
frame = 0

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE, frames_per_buffer=CHUNK, output=True)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Theremin")

kb = kbhit.KBHit()

while frame < endFrame:
    
    samples = np.zeros(CHUNK,dtype=np.float32)

    c= ' '
    if kb.kbhit():
        c = kb.getch()
        if (c=='f'): fm = max(0,fm - 5)
        elif (c=='F'): fm = fm + 5
        if (c=='b'): beta = max(0,beta - 1)
        elif (c=='B'): beta = beta + 1
        print('\n')
        print("FC = ", fc)
        print("Vol = ", vol)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEMOTION:
            mouseX, mouseY = event.pos
            fc = (mouseX*maxFrec)/WIDTH
            vol = (mouseY*maxVol)/HEIGHT

    samples = samples+oscFM(fc,fm,beta, vol,frame)
        
    samples = samples * envSamples[frame:frame+CHUNK]
    frame += CHUNK
    stream.write(samples.tobytes())