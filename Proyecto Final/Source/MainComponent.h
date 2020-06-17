
#pragma once

//==============================================================================
class MainContentComponent : public AudioAppComponent,
    public ChangeListener
{
public:
    MainContentComponent()
        : state(Stopped),
        forwardFFT(fftOrder)
    {
        //SETUP BOTONS
        addAndMakeVisible(&openButton);
        openButton.setButtonText("Open mp3/wav file");
        openButton.onClick = [this] { openButtonClicked(); };

        addAndMakeVisible(&playButton);
        playButton.setButtonText("Play the audio");
        playButton.onClick = [this] { playButtonClicked(); };
        playButton.setColour(TextButton::buttonColourId, Colours::green);
        playButton.setEnabled(false);

        addAndMakeVisible(&stopButton);
        stopButton.setButtonText("Stop the audio");
        stopButton.onClick = [this] { stopButtonClicked(); };
        stopButton.setColour(TextButton::buttonColourId, Colours::red);
        stopButton.setEnabled(false);

        addAndMakeVisible(&midiButton);
        midiButton.setButtonText("Convert to midi");
        midiButton.onClick = [this] { midiButtonClicked(); };
        midiButton.setColour(TextButton::buttonColourId, Colours::blue);
        midiButton.setEnabled(false);
        setSize(800, 600);

        addAndMakeVisible(audioSelector);

        //SELECCIONAR TIPO DE AUDIO
        audioSelector.addItem("mp3", 1);
        audioSelector.addItem("wav", 2);
        audioSelector.setSelectedId(1);
        audioSelector.onChange = [this] {
            switch (audioSelector.getSelectedId())
        {
            case 1:  currentAudio = "mp3";  break;
            case 2:   currentAudio = "wav";   break;
        }};
        formatManager.registerBasicFormats(); 
        transportSource.addChangeListener(this); 
        currentNote = 0; //al empezar no hay nota
        fillNotes(); //mapeamos las notas
        startTime = 0; //empiezo en 0
        setAudioChannels(0, 2);//sin canales de entrada y si de salida
    }

    ~MainContentComponent() override
    {
        shutdownAudio();
    }

    void prepareToPlay(int samplesPerBlockExpected, double sampleRate) override
    {
        transportSource.prepareToPlay(samplesPerBlockExpected, sampleRate); //para reproducir el audio
    }
    void fillNotes() {
        mapNotes.set(7, 155.56); //RE#3
        mapNotes.set(700, 164.81); //MI3 
        mapNotes.set(8, 174.61); //FA3
        mapNotes.set(800, 185); //FA#3 
        mapNotes.set(80000, 196); //SOL3 Cuidao
        mapNotes.set(9, 207.65); //SOL#3 Cuidao
        mapNotes.set(900, 220); //LA3 
        mapNotes.set(10, 233.08); //LA#3 
        mapNotes.set(11, 246.94); //SI3 
        mapNotes.set(1100, 261.63); //DO4
        mapNotes.set(12, 277.18); //DO#4 
        mapNotes.set(13, 293.66); //RE4 
        mapNotes.set(1300, 311.13); //RE#4 
        mapNotes.set(14, 329.63); //MI4
        mapNotes.set(15, 349.23); //FA4
        mapNotes.set(16, 369.99); //FA#4
        mapNotes.set(17, 392); //SOL4
        mapNotes.set(18, 415.3); //SOL#4 
        mapNotes.set(19, 440); //LA4
        mapNotes.set(20, 466.16); //LA#4
        mapNotes.set(21, 493.88); //SI4
        mapNotes.set(22, 523.25); //DO5
        mapNotes.set(24, 554.37); //DO#5
        mapNotes.set(25, 587.33); //RE5
        mapNotes.set(26, 622.25); //RE#5
        mapNotes.set(28, 659.25); //MI5
        mapNotes.set(30, 698.46); //FA5 
        mapNotes.set(32, 739.99); //FA#5 
        mapNotes.set(34, 783.99); //SOL5
        mapNotes.set(36, 830.61); //SOL#5 
        mapNotes.set(37, 880); //LA5
        mapNotes.set(38, 880); //LA5 marcado
        mapNotes.set(39, 880); //LA5
        mapNotes.set(40, 932.33); //LA#5 marcado
        mapNotes.set(41, 932.33); //LA#5
        mapNotes.set(42, 932.33); //LA#5
        mapNotes.set(43, 987.77); //SI5 
        mapNotes.set(44, 987.77); //SI5 
        mapNotes.set(45, 1046.5); //DO6 
    }
    void getNextAudioBlock(const AudioSourceChannelInfo& bufferToFill) override
    {
        if (readerSource.get() == nullptr) //si hemos acabado
        {
            bufferToFill.clearActiveBufferRegion();
            return;
        }

        transportSource.getNextAudioBlock(bufferToFill); //siguiente bloque

        for (auto channel = 0; channel < 1; ++channel)
        {
            auto* inBuffer = bufferToFill.buffer->getReadPointer(channel,
                bufferToFill.startSample);
            auto* outBuffer = bufferToFill.buffer->getWritePointer(channel, bufferToFill.startSample);
            for (auto sample = 0; sample < bufferToFill.numSamples; ++sample)
                pushNextSampleIntoFifo(inBuffer[sample]); //meto las samples del bloque al fifo
        }
        double sampleRate = 44100;
        double freq = mapNotes.operator[](trueMax()); //averiguamos la frecuencia del bloque a traves de un analisis nuestro que realiza trueMax()
        int m = round(((log(freq * 32 / 440) / log(2)) * 12) + 9); //transformo esa frecuencia al numero de nota que es para construir despues el mensaje midi (ej. do3 = 48)
        if (nextFFTBlockReady) //para no perder informacion
        {      
            forwardFFT.performFrequencyOnlyForwardTransform(fftData); //aplico la transformada de fourier (ver memoria para explicacion)
            nextFFTBlockReady = false;
        }
       
        if (trueMax() == 0 && currentNote != 0 ) { //caso particular de nuestro analisis, que si devuelve 0 quiere decir que no hay sonido
            endNote(currentNote);
            currentNote = 0;
        }
        if (currentNote != m && freq < 1500 && m >= 0 && freq > 0) { //si tengo una nota distinta a la que habia con una frecuencia y numero de nota valido, termino la anterior y empiezo la nueva
            if (currentNote != 0) {
                endNote(currentNote); //terminar la nota
            }
            newNote(m); //empiezo nota nueva
            currentNote = m; //ahora la nota actual es la nueva
        }
        startTime = startTime + (bufferToFill.numSamples / sampleRate); //num_samples = 480, esto es el tiempo en segundos al que equivale un bloque

    }
    void newNote(int note) {
        int velocity = 100;
        MidiMessage m(MidiMessage::noteOn(1, note, (uint8)velocity)); //creo mensaje de tipo midi de que empieza nota

        m.setTimeStamp((startTime*1000)*0.2); //le asigno un lugar en el tiempo y multiplico por la constante 0.2 para transformar de milisegundos a beats
        sequence.addEvent(m); //añado este mensaje a una lista
    }
    void endNote(int note) {
        int velocity = 100;
        MidiMessage m(MidiMessage::noteOff(1, note, (uint8)velocity)); //creo mensaje de tipo midi de que empieza nota
        m.setTimeStamp((startTime*1000)*0.2); //le asigno un lugar en el tiempo y multiplico por la constante 0.2 para transformar de milisegundos a beats
        sequence.addEvent(m);  //añado este mensaje a una lista

    }
    void pushNextSampleIntoFifo(float sample) noexcept //relleno fftData con politica first in first out
    {
        if (fifoIndex == fftSize)
        {
            if (!nextFFTBlockReady)
            {
                zeromem(fftData, sizeof(fftData));
                memcpy(fftData, fifo, sizeof(fifo));
                nextFFTBlockReady = true;
            }
            fifoIndex = 0;
        }

        fifo[fifoIndex++] = sample;
    }

    
    double trueMax() { //analisis de la transformada
        int umbral = 30;
        double empty = fftData[0];
        for (int i = 1; i < fftSize / 2; i++) {
            empty = empty + fftData[i];
            if (fftData[i] < 0) { //si tengo una onda y no la transformada quiere decir que sigo en la misma nota, -1 equivale a no hacer nada con el bloque
                return -1;
            }
            if (fftData[i] > fftData[i + 1] && fftData[i] > fftData[i - 1]) { //observo un pico dentro de la fft
                //Cuanto mas alto sea el indice en el que encuentro un pico, cuyo valor debe ser mayor que un umbral que determina dicho indice, mas alta sera la nota
                //Existen casos particulares (mas que particulares cuando la nota es muy grave) en los que un mismo indice de pico corresponde a varias notas, en cuyo caso lo distinguimos en funcion 
                //de la distancia del siguiente pico, es complejo de ver en el codigo, vease NotasMapaConceptual o en la defensa de este proyecto oralmente

                if (i <= 11 && fftData[i] > 20) {
                    if (i == 7) {
                        if (fftData[14] > 120) {
                            return i * 100;
                        }
                        else {
                            return i;
                        }
                    }
                    if (i == 8) {
                        if (fftData[15] > 150) {
                            return i;
                        }
                        else if (fftData[16] > 100) {
                            return i * 100;
                        } 
                        else{
                            return i * 10000;
                        }
                    }
                    if (i == 9) {
                        if (fftData[18] > 150) {
                            return i;
                        }
                        else {
                            return i*100;
                        }
                    }
                    if (i == 11) {
                        if (fftData[21] > 80) {
                            return i;
                        }
                        else {
                            return i*100;
                        }
                    }
                    return i;
                }

                if (i > 11 && i < 22 && fftData[i] > 42) {
                    if (i == 13) {
                        if (fftData[25] > 50) {
                            return i;
                        }
                        else {
                            return i * 100;
                        }
                    }
                    return i;
                }
                if (i >= 22 && i < 50 && fftData[i] > 100) { //a partir de ciertas notas agudas el problema del indice no ocurre, por eso nuestro programa es mas exacto cuanto mas agudo
                    return i;
                }
            }
        }
        if (empty < 2) { //si la suma de los valores de la transformada es <2 quiere decir que no hay sonido, o es despreciable
            return 0;
        }
        return -1;
       
    }


    void releaseResources() override
    {
        transportSource.releaseResources();
    }

    void resized() override  //defino los bordes de los botones, puramente visual
    {
        openButton.setBounds(20, 20, 640, 40);
        audioSelector.setBounds(680, 20, 80, 40);
        playButton.setBounds(20, 80, 760, 40);
        stopButton.setBounds(20, 140, 760, 40);
        midiButton.setBounds(20, 200, 760, 40);
    }

    void changeListenerCallback(ChangeBroadcaster* source) override //introduzco instrucciones mientras este sonando algo, cuando pare puede escribirse a archivo
    {
        if (source == &transportSource)
        {
            if (transportSource.isPlaying())
                changeState(Playing);
            else {
                changeState(Stopped);
                midiButton.setEnabled(true);
            }
        }
    }

private:
    enum
    {
        fftOrder =11,
        fftSize = 1 << fftOrder,
        scopeSize = 1024
    };
    enum TransportState
    {
        Stopped,
        Starting,
        Playing,
        Stopping
    };

    void changeState(TransportState newState) //en que estado estoy de la reproduccion, para no poder reproducir si no tengo archivo disponible, por ejemplo
    {
        if (state != newState)
        {
            state = newState;

            switch (state)
            {
            case Stopped:
                stopButton.setEnabled(false);
                playButton.setEnabled(true);
                transportSource.setPosition(0.0);
                break;

            case Starting:
                playButton.setEnabled(false);
                transportSource.start();
                break;

            case Playing:
                stopButton.setEnabled(true);
                break;

            case Stopping:
                transportSource.stop();
                break;
            }
        }
    }

    void openButtonClicked()
    {
        //reseteo todo lo que hubiese hecho antes porque tengo un archivo nuevo
        sequence.clear();
        zeromem(fftData, sizeof(fftData));
        zeromem(fifo, sizeof(fifo));
        fifoIndex = 0;
        startTime = 0;
        FileChooser chooser("Select an audio file to play...",
            {},
            "*."+currentAudio);

        if (chooser.browseForFileToOpen())
        {
            auto file = chooser.getResult();
            auto* reader = formatManager.createReaderFor(file);

            if (reader != nullptr)
            {
                std::unique_ptr<AudioFormatReaderSource> newSource(new AudioFormatReaderSource(reader, true));
                transportSource.setSource(newSource.get(), 0, nullptr, reader->sampleRate);
                playButton.setEnabled(true);
                readerSource.reset(newSource.release());
            }
        }
    }

    void playButtonClicked()
    {
        changeState(Starting);
    }
    void midiButtonClicked() //guardar el archivo midi
    {
        
        File fi;
        FileChooser chooser("Select a name...",
            {},
            "*.mid");

        if (chooser.browseForFileToSave(true))
        {
            fi = chooser.getResult();
            auto* reader = formatManager.createReaderFor(fi);
        }

        MidiFile mfile;
        FileOutputStream stream = fi;
        mfile.setTicksPerQuarterNote(100);
        mfile.addTrack(sequence); //añado los mensaje de la lista
        mfile.writeTo(stream);

    }
    void stopButtonClicked()
    {
        changeState(Stopping);
    }

    //==========================================================================
    TextButton openButton;
    TextButton playButton;
    TextButton stopButton;
    TextButton midiButton;
    Random random;
    AudioFormatManager formatManager;
    std::unique_ptr<AudioFormatReaderSource> readerSource;
    AudioTransportSource transportSource;
    TransportState state;
    MidiMessageSequence sequence;
    dsp::FFT forwardFFT;
    float fifo[fftSize];
    float fftData[2 * fftSize];
    int fifoIndex = 0;
    bool nextFFTBlockReady = false;
    int currentNote;
    double startTime;
    float high;
    HashMap<int, double> mapNotes;
    int fftIndex;
    String currentAudio = "mp3"; //por defecto supongo que el archivo es mp3
    ComboBox audioSelector;
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MainContentComponent)
};
