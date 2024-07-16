from PyQt6 import QtWidgets
from PyQt6.QtGui import QEnterEvent
from PyQt6.QtGui import QKeySequence, QShortcut
import sys
import pyaudio
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

# Create a PyAudio stream for recording
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
channels=CHANNELS,
rate=RATE,
input=True,
frames_per_buffer=CHUNK)
frames = []

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('oxxo.studio')
        self.resize(300, 200)
        self.setMouseTracking(True)
        self.ui()

    def ui(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(20,20,100,30)
        # shortcut_S = QShortcut(QKeySequence("Ctrl+S"), self)
        # shortcut_S.activated.connect(self.voiceStart)

    def keyPressEvent(self, event):
        key = event.key()             # 取得該按鍵的 keycode
        self.label.setText(str(key))  # QLabel 印出 keycode
        if(key==32):
            print("hello")


    def voiceStart(self):
        print("Listening...Press q to terminate Voice Input")
        data = stream.read(CHUNK)
        frames.append(data)
        wave_file = wave.open("test.wav", 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(p.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()
        print("Voice Input Ended")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Form = MyWidget()
    Form.show()
    sys.exit(app.exec())