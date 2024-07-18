def fazalgo(teste):
    print(teste)

import pyaudio
import wave

audio = pyaudio.PyAudio()

stream = audio.open(
    input=True,
    format=pyaudio.paInt16,
    channels=1,
    rate=44000,
    frames_per_buffer=1024,
)

frames = []

try:
    while True:
        bloco = stream.read(1024)
        frames.append(bloco)
except KeyboardInterrupt:
    pass

stream.start_stream()
stream.close()
audio.terminate()

arquivo_final = wave.open("gravacao.wav", "wb")
arquivo_final.setnchannels(1)
arquivo_final.setframerate(44000)
arquivo_final.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
arquivo_final.writeframes(b"".join(frames))
arquivo_final.close()