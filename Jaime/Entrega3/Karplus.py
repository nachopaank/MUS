import numpy as np
import pyaudio, kbhit
from scipy.io import wavfile


p = pyaudio.PyAudio()
RATE = 44100
c = ''
CHUNK = 1024
kb = kbhit.KBHit()
numbloque = 0
fs = 8000


stream2 = p.open(format = pyaudio.paFloat32,
                channels = 2,
                rate = fs,
                frames_per_buffer = CHUNK,
                output = True)

def karplus_strong(wavetable, n_samples):
    """Synthesizes a new waveform from an existing wavetable, modifies last sample by averaging."""
    samples = []
    current_sample = 0
    previous_value = 0
    while len(samples) < n_samples:
        wavetable[current_sample] = 0.5 * (wavetable[current_sample] + previous_value)
        samples.append(wavetable[current_sample])
        previous_value = samples[-1]
        current_sample += 1
        current_sample = current_sample % wavetable.size
    return np.array(samples)

dataPlay = np.zeros(0,dtype=int)
freqs = np.logspace(0, 1, num=12, base=2) * 55
multi = False

def cal_wavetable(size):
    wavetable_size = fs // int(size) 
    np.random.seed(1)
    return (2 * np.random.randint(0, 2, wavetable_size) - 1).astype(np.float32)

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
    stream2.write(bloque.astype((np.float32)).tobytes())
    bloqueAux = numbloque
    dataAux = dataPlay
    if kb.kbhit():
        c = kb.getch()    
        if c == 'z':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[0]), 2*fs)
        elif c == 'x':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[2]), 2*fs)
        elif c == 'c':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[4]), 2*fs)
        elif c == 'v':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[5]), 2*fs)
        elif c == 'b':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[7]), 2*fs)
        elif c == 'n':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[9]), 2*fs)
        elif c == 'm':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[11]), 2*fs)
        elif c == 's':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[1]), 2*fs)
        elif c == 'd':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[3]), 2*fs)
        elif c == 'g':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[6]), 2*fs)
        elif c == 'h':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[8]), 2*fs)
        elif c == 'j':
            numbloque = 0
            dataPlay = karplus_strong(cal_wavetable(freqs[10]), 2*fs)

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
stream2.stop_stream()
stream2.close()
p.terminate()
