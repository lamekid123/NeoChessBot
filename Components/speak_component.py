import pyttsx3
import threading
import queue
import time

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
        self.tts_engine.setProperty("voice", "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
        self.tts_engine.startLoop(False)
        self.start()

    def run(self):
        print("TTS running")
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