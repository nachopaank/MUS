import sys
import pygame
from pygame.locals import *
import numpy as np
import pyaudio, kbhit
from scipy.io import wavfile
import os
from ctypes import windll, Structure, c_long, byref
import tkinter

"""
class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]



def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return { pt.x, pt.y}

import logging
import sys

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG,
                    stream=sys.stdout)


def get_mouse_position():
    Get the current position of the mouse.

    Returns
    -------
    dict :
        With keys 'x' and 'y'
    mouse_position = None
    import sys
    if sys.platform in ['linux', 'linux2']:
        pass
    elif sys.platform == 'Windows':
        try:
            import win32api
        except ImportError:
            logging.info("win32api not installed")
            win32api = None
        if win32api is not None:
            x, y = win32api.GetCursorPos()
            mouse_position = {'x': x, 'y': y}
    elif sys.platform == 'Mac':
        pass
    else:
        try:
            import Tkinter  # Tkinter could be supported by all systems
        except ImportError:
            logging.info("Tkinter not installed")
            Tkinter = None
        if Tkinter is not None:
            p = Tkinter.Tk()
            x, y = p.winfo_pointerxy()
            mouse_position = {'x': x, 'y': y}
        print("sys.platform={platform} is unknown. Please report."
              .format(platform=sys.platform))
        print(sys.version)
    return mouse_position
"""


WIDTH = 480
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Theremin")


RATE= 44100
CHUNK = 1024
p = pyaudio.PyAudio()
kb = kbhit.KBHit()
c = ' '
clear = lambda: os.system('cls')

stream = p.open(format = pyaudio.paFloat32,
                channels = 1,
                rate = RATE,
                frames_per_buffer = CHUNK,
                output = True)

def oscFM(fc,fm,beta,vol,frame):
    interval = np.arange(CHUNK)+frame # array para el chunk
    mod = (RATE*beta)*np.sin(2*np.pi*fm*interval/RATE) # moduladora
    res = np.sin((2*np.pi*fc*interval+mod)/RATE) # portadora
    return vol*res
# tabla de ondas -> se copia la tabla cíclicamente hasta rellenenar un CHUNK
def synthWaveTable(wavetable, frame):
    samples = np.zeros(CHUNK, dtype=np.float32) 
    t = frame % (len(wavetable))
    #t = 0
    for i in range(CHUNK):
        samples[i] = wavetable[t]
        t = (t+1) % len(wavetable)
        
    return samples
def nextF(fIni,fFin):
    if (fIni < fFin):
        return fIni+1
    elif (fIni > fFin):
        return fIni-1
    return fIni
# tabla de ondas para un seno de 800 Hz: se almacena un ciclo
frec = 800
waveTable = np.sin(2*np.pi*frec*np.arange(RATE/frec,dtype=np.float32)/RATE)
fc = 440
fm = 300
beta = 1
vol = 1
frame = 0
preFrec = 440
postFrec = 440
p=tkinter.Tk()
while c != 'q':   
    samples = synthWaveTable(oscFM(fc,fm,beta,vol,frame),frame)
    stream.write(samples.tobytes())
    frame += CHUNK
   
    if kb.kbhit(): 
        c = kb.getch()
        if c == 'F':
            fc = fc + 1
        elif c == 'f':
            fc = fc - 1
        elif c == 'G':
            clear()
            fm = fm + 1
        elif c == 'g':
            fm = fm - 1
        elif c == 'H':
            beta = beta + 0.5
        elif c == 'h':
            beta = beta - 0.5
        elif c == 'J':
            vol = vol + 0.05
        elif c == 'j':
            vol = vol - 0.05
        clear()
        
        print("Fc = ", fc)       
        print("Fm: ", fm)
        print("Beta: ", beta)
        print("Vol: ", vol)
    #p=tkinter.Tk()
    for event in pygame.event.get():
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
    #x, y = p.winfo_pointerxy()
    fc = x/WIDTH*1000
    vol = y/HEIGHT 
pygame.quit()

kb.set_normal_term()
stream.stop_stream()
stream.close()
kb.set_normal_term()
p.terminate()
