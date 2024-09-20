import time
import random
import TTS.model
import pyaudio
import wave


import time
import random
import wave
import struct
import pyttsx3
import torch

import torch
from TTS.api import TTS

from TTS.tts.configs.tortoise_config import TortoiseConfig
from TTS.tts.models.tortoise import Tortoise

def tts(text):
   config = TortoiseConfig()
   model = Tortoise.init_from_config(config)
   model.load_checkpoint(config, checkpoint_dir="paths/to/models_dir/", eval=True)


   # cloning a speaker
   output_dict = model.synthesize(text, config, speaker_id="speaker_n", extra_voice_dirs="path/to/speaker_n/")
   return output_dict

def gravar_amostra_voz(duracao=20, taxa_amostragem=44100, canais=1, formato=pyaudio.paInt16):
   print("Preparando para gravar a amostra de voz...")
  
   # Configurar PyAudio
   p = pyaudio.PyAudio()
  
   # Abrir stream
   stream = p.open(format=formato,
                   channels=canais,
                   rate=taxa_amostragem,
                   input=True,
                   frames_per_buffer=1024)
  
   print("Gravação iniciada. Fale por 20 segundos...")
  
   frames = []
   for i in range(0, int(taxa_amostragem / 1024 * duracao)):
       data = stream.read(1024)
       frames.append(data)
       if i % 43 == 0:  # Aproximadamente a cada segundo
           print(f"Gravando... {i // 43 + 1} segundos")
  
   print("Gravação concluída.")
  
   # Parar e fechar o stream
   stream.stop_stream()
   stream.close()
   p.terminate()
  
   # Salvar o arquivo de áudio
   nome_arquivo = f"amostra_voz_{int(time.time())}.wav"
   wf = wave.open(nome_arquivo, 'wb')
   wf.setnchannels(canais)
   wf.setsampwidth(p.get_sample_size(formato))
   wf.setframerate(taxa_amostragem)
   wf.writeframes(b''.join(frames))
   wf.close()
  
   print(f"Amostra de voz salva como {nome_arquivo}")
   return nome_arquivo

def clone_voice(voice_sample):
   if len(voice_sample) < 20:
       raise ValueError("A amostra de voz deve ter pelo menos 20 segundos.")
  
   print("Iniciando o processo de clonagem de voz...")
   time.sleep(2)  # Simulando processamento
  
   # Simulando etapas de clonagem
   print("Analisando características vocais...")
   time.sleep(1)
   print("Extraindo parâmetros de frequência...")
   time.sleep(1)
   print("Modelando entonação e ritmo...")
   time.sleep(1)
   print("Gerando modelo de voz sintética...")
   time.sleep(2)
  
   # Simulando qualidade do clone
   quality = random.uniform(0.7, 0.99)
  
   print(f"Clone de voz criado com sucesso! Qualidade estimada: {quality:.2%}")
  
   return {
       "clone_id": f"voice_clone_{int(time.time())}",
       "quality": quality,
       "sample_length": len(voice_sample),
       "is_ready": True
   }


# arquivo_amostra = gravar_amostra_voz()

text = "Note that the server is not optimized for performance but gives you an easy way to interact with the models"

# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# # generate speech by cloning a voice using default settings
# tts.tts_to_file(text="It took me quite a long time to develop a voice, and now that I have it I'm not going to be silent.",
#                 file_path="output.wav",
#                 speaker_wav=["/home/luzia-tpv/Documentos/Estudos/aistudy/amostra_voz_1726797442.wav"],
#                 language="en",
#                 split_sentences=True
#                 )

# print(torch.cuda.is_available())

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"


# List available 🐸TTS models
print(TTS().list_models())


# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)


# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# Text to speech to a file
tts.tts_to_file(text=text, speaker_wav="/home/luzia-tpv/Documentos/Estudos/aistudy/amostra_voz_1726797442.wav", language="en", file_path="output.wav")