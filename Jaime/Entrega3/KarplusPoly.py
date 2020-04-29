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

stream = p.open(format = pyaudio.paFloat32,
                channels = 2,
                rate = fs,
                frames_per_buffer = CHUNK,
                output = True)

stream2 = p.open(format = pyaudio.paFloat32,
                channels = 2,
                rate = fs,
                frames_per_buffer = CHUNK,
                output = True)

stream3 = p.open(format = pyaudio.paFloat32,
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


freqs = np.logspace(0, 1, num=12, base=2) * 55

def cal_wavetable(size):
    wavetable_size = fs // int(size)
    np.random.seed(1)
    return (2 * np.random.randint(0, 2, wavetable_size) - 1).astype(np.float32)

arrayBool = [False,True,True]
arrayNum = [0,0,0]
arrayData = [np.zeros(0,dtype=int),np.zeros(0,dtype=int),np.zeros(0,dtype=int)]
cAux='q'

while c != 'q':
    i=0
    stream.write(arrayData[1][arrayNum[1]*CHUNK:arrayNum[1]*CHUNK+CHUNK].astype((np.float32)).tobytes())
    stream2.write(arrayData[0][arrayNum[0]*CHUNK:arrayNum[0]*CHUNK+CHUNK].astype((np.float32)).tobytes())
    stream3.write(arrayData[2][arrayNum[2]*CHUNK:arrayNum[2]*CHUNK+CHUNK].astype((np.float32)).tobytes())

    if kb.kbhit():
        c = kb.getch()    
        if c == 'z':
            dataAux = karplus_strong(cal_wavetable(freqs[0]), 2*fs)
        elif c == 'x':
            dataAux = karplus_strong(cal_wavetable(freqs[2]), 2*fs)
        elif c == 'c':
            dataAux = karplus_strong(cal_wavetable(freqs[4]), 2*fs)
        elif c == 'v':
            dataAux = karplus_strong(cal_wavetable(freqs[5]), 2*fs)
        elif c == 'b':
            dataAux = karplus_strong(cal_wavetable(freqs[7]), 2*fs)
        elif c == 'n':
            dataAux = karplus_strong(cal_wavetable(freqs[9]), 2*fs)
        elif c == 'm':
            dataAux = karplus_strong(cal_wavetable(freqs[11]), 2*fs)
        elif c == 's':
            dataAux = karplus_strong(cal_wavetable(freqs[1]), 2*fs)
        elif c == 'd':
            dataAux = karplus_strong(cal_wavetable(freqs[3]), 2*fs)
        elif c == 'g':
            dataAux = karplus_strong(cal_wavetable(freqs[6]), 2*fs)
        elif c == 'h':
            dataAux = karplus_strong(cal_wavetable(freqs[8]), 2*fs)
        elif c == 'j':
            dataAux = karplus_strong(cal_wavetable(freqs[10]), 2*fs)

        
        for x in arrayBool:
            if not(x):
                if c!=cAux:
                    arrayBool[i] = True
                    arrayNum[i] = 0
                    arrayData[i] = dataAux
                    #print("Asignado a ",i)
                    arrayBool[(i+1)%len(arrayBool)]=False
                    break
                else:
                    arrayNum[(i-1)%len(arrayNum)] = 0
            i+=1
        

        cAux=c
    
    for i in range(len(arrayNum)):
        arrayNum[i] += 1
        i+=1
    


kb.set_normal_term()
stream.stop_stream()
stream.close()
stream2.stop_stream()
stream2.close()
p.terminate()
