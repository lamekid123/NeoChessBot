import pyttsx3
import threading
import queue
import time
import pyaudio
import wave
import keyboard

## Text-to-speech engine that run in another thread
class TTSThread(threading.Thread):

    ##auto start and loop until application close
    def __init__(self):
        threading.Thread.__init__(self)
        self.importance = False
        self.queue = queue.Queue()
        self.daemon = True
        self.tts_engine = pyttsx3.init("sapi5")    ## sapi5 for Windows, nsss for Mac, espeak for others
        self.tts_engine.setProperty("rate", 190)
        self.tts_engine.setProperty("volume", 0.7)
        self.tts_engine.startLoop(False)
        self.start()

    def run(self):
        self.tts_engine.iterate()
        t_running = True
        while t_running:
            if self.queue.empty():
                self.tts_engine.iterate()
            else:

                data = self.queue.get()
                self.tts_engine.stop()
                self.tts_engine.say(data[0])

                ##when the message's important flag = true -> can not be interrupt
                if data[1] == True:
                    time.sleep(2)

        self.tts_engine.endLoop()

class S2TThread(threading.Thread):

    ##auto start and loop until application close
    def __init__(self):
        threading.Thread.__init__(self)
        self.input = "test.wav"
        self.daemon = True
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.FRAME)
        self.frames = []
        self.start()

    def run(self):
        voiceInput_running = True
        while voiceInput_running:
            while(keyboard.is_pressed('space')):
                data = self.stream.read(self.CHUNK)
                self.frames.append(data)
            if(not self.frames):
                wave_file = wave.open("test.wav", 'wb')
                wave_file.setnchannels(self.CHANNELS)
                wave_file.setsampwidth(self.p.get_sample_size(self.FORMAT))
                wave_file.setframerate(self.RATE)
                wave_file.writeframes(b''.join(self.frames))
                wave_file.close()
                self.frames=[]
                print("Voice Input Ended")
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
