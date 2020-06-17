#pragma once


//==============================================================================

using namespace dsp;

class MainContentComponent : public AudioAppComponent,
    public ChangeListener
{
public:
    MainContentComponent()
        : state(Stopped)
    {
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

        formatManager.registerBasicFormats();       // [1]
        transportSource.addChangeListener(this);   // [2]

        setAudioChannels(0, 2);
    }

    ~MainContentComponent() override
    {
        shutdownAudio();
    }

    void prepareToPlay(int samplesPerBlockExpected, double sampleRate) override
    {
        transportSource.prepareToPlay(samplesPerBlockExpected, sampleRate);
    }

    void getNextAudioBlock(const AudioSourceChannelInfo& bufferToFill) override
    {
        if (readerSource.get() == nullptr)
        {
            bufferToFill.clearActiveBufferRegion();
            return;
        }
        transportSource.getNextAudioBlock(bufferToFill);

        FFT wow = STFT(bufferToFill, 256);



        for (auto channel = 0; channel < 1; ++channel)
        {
            auto* inBuffer = bufferToFill.buffer->getReadPointer(channel,
                bufferToFill.startSample);
            auto* outBuffer = bufferToFill.buffer->getWritePointer(channel, bufferToFill.startSample);
            for (auto sample = 0; sample < bufferToFill.numSamples; ++sample) {
                //outBuffer[sample] = inBuffer[sample] * random.nextFloat() * level;
            }
        }
        ///
        //analyze();
        ///

    }
    dsp::FFT STFT(const AudioSourceChannelInfo& bufferToFill, size_t hop) {
        const float* data = bufferToFill.buffer->getReadPointer(0);
        const size_t dataCount = bufferToFill.buffer->getNumSamples();

        // fftSize will be the number of bins we used to initialize the ASpectroMaker.
        ptrdiff_t fftSize = forwardFFT.getSize();

        // forwardFFT works on the data in place, and needs twice as much space as the input size.
        std::vector<float> fftBuffer(fftSize * 2UL);

        // While data remains

        {
            std::memcpy(fftBuffer.data(), data, fftSize * sizeof(float));

            // prepare fft data...

            forwardFFT.performFrequencyOnlyForwardTransform(fftBuffer.data());

            // ...copy the frequency information from fftBuffer to the spectrum

            // Next chunk
            data += hop;
        }

        return forwardFFT;
        //...
    }
    void analyze() {
        int cuando;
        int nota;
        int velocity = 100;
        //aqui esto
        MidiMessage m(MidiMessage::noteOn(1, nota, (uint8)velocity));
        m.setTimeStamp(cuando);
        sequence.addEvent(m);
    }

    void releaseResources() override
    {
        transportSource.releaseResources();
    }

    void resized() override
    {
        openButton.setBounds(20, 20, 760, 40);
        playButton.setBounds(20, 80, 760, 40);
        stopButton.setBounds(20, 140, 760, 40);
        midiButton.setBounds(20, 200, 760, 40);
    }

    void changeListenerCallback(ChangeBroadcaster* source) override
    {
        if (source == &transportSource)
        {
            if (transportSource.isPlaying())
                changeState(Playing);
            else
                changeState(Stopped);
        }
    }

private:
    enum TransportState
    {
        Stopped,
        Starting,
        Playing,
        Stopping,
        Noising
    };

    void changeState(TransportState newState)
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
        FileChooser chooser("Select a mp3 file to play...",
            {},
            "*.mp3");

        if (chooser.browseForFileToOpen())
        {
            auto file = chooser.getResult();
            auto* reader = formatManager.createReaderFor(file);

            if (reader != nullptr)
            {
                std::unique_ptr<AudioFormatReaderSource> newSource(new AudioFormatReaderSource(reader, true));
                transportSource.setSource(newSource.get(), 0, nullptr, reader->sampleRate);
                playButton.setEnabled(true);
                midiButton.setEnabled(true);
                readerSource.reset(newSource.release());
            }
        }
    }

    void playButtonClicked()
    {
        changeState(Starting);
    }
    void midiButtonClicked()
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
        /*
        MidiMessage m(MidiMessage::noteOn(1, 30, (uint8)100));
        m.setTimeStamp(0);
        sequence.addEvent(m);
        MidiMessage m2(MidiMessage::noteOn(1, 5, (uint8)100));
        m2.setTimeStamp(0);
        sequence.addEvent(m2);
        MidiMessage m3(MidiMessage::noteOn(1, 10, (uint8)50));
        m3.setTimeStamp(0);
        sequence.addEvent(m3);
        sequence.updateMatchedPairs();
        MidiMessage m4(MidiMessage::noteOn(1, 15, (uint8)100));
        m4.setTimeStamp(0);
        sequence.addEvent(m4);
        MidiMessage m5(MidiMessage::noteOn(1, 25, (uint8)100));
        m5.setTimeStamp(0);
        sequence.addEvent(m5);
        MidiMessage m6(MidiMessage::noteOff(1, 30, (uint8)100));
        m6.setTimeStamp(300);
        sequence.addEvent(m6);
        MidiMessage m7(MidiMessage::noteOff(1, 5, (uint8)100));
        m7.setTimeStamp(300);
        sequence.addEvent(m7);
        MidiMessage m8(MidiMessage::noteOff(1, 10, (uint8)50));
        m8.setTimeStamp(400);
        sequence.addEvent(m8);
        MidiMessage m9(MidiMessage::noteOff(1, 15, (uint8)100));
        m9.setTimeStamp(400);
        sequence.addEvent(m9);
        MidiMessage m10(MidiMessage::noteOff(1, 25, (uint8)100));
        m10.setTimeStamp(400);
        sequence.addEvent(m10);
        sequence.updateMatchedPairs();
        */
        mfile.setTicksPerQuarterNote(100);
        mfile.addTrack(sequence);
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
    Label levelLabel;
    Random random;
    AudioFormatManager formatManager;
    std::unique_ptr<AudioFormatReaderSource> readerSource;
    AudioTransportSource transportSource;
    TransportState state;
    MidiMessageSequence sequence;


    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MainContentComponent)
};
