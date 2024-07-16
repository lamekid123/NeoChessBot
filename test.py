import whisper
import pyaudio
import keyboard

model = whisper.load_model("base")
import pyaudio
import wave
import keyboard

# Recording parameters
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

def recording():
    recording = True
    while(recording == True):
        print("Recording started...")
        data = stream.read(frames)
        frames.append(data)
        if(keyboard.is_pressed("r")):
            recording = False
    print("Recording Stopped")
    wave_file = wave.open("test.wav", 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(p.get_sample_size(FORMAT))
    wave_file.setframerate(RATE)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()
    return 0


keyboard.add_hotkey("r", recording)

# Register the key press events
while(True):
    print("yeahyeah waiting u test")
    keyboard.wait()
    
    result = model.transcribe("test.wav")

    print(result["text"])
    # Stop and close the PyAudio stream


# while(keyboard.is_pressed('r')):
#     print("recording")
    
    # result = model.transcribe("h5_g5.mp3")

    # print(result["text"])

stream.stop_stream()
stream.close()
p.terminate()