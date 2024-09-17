import time
import random
import pyaudio
import wave

import time
import random
import wave
import struct

# def texto_para_audio_clonado(texto, voz_clonada):
#     print(f"Convertendo texto para áudio usando a voz clonada: {voz_clonada['clone_id']}")
    
#     # Simulando o processo de síntese de voz
#     print("Analisando o texto...")
#     time.sleep(1)
#     print("Aplicando regras de pronúncia...")
#     time.sleep(1)
#     print("Gerando fonemas...")
#     time.sleep(1)
#     print("Sintetizando áudio com a voz clonada...")
#     time.sleep(2)
    
#     # Calculando a duração estimada do áudio (simulação simplificada)
#     palavras = texto.split()
#     duracao_estimada = len(palavras) * 0.5  # Estimativa grosseira de 0.5 segundos por palavra
    
#     # Gerando um arquivo de áudio simples para simular o resultado
#     nome_arquivo = f"audio_sintetizado_{int(time.time())}.wav"
    
#     # Parâmetros do áudio
#     framerate = 44100
#     amplitude = 8000
#     frequencia = 440.0
    
#     # Gerando dados de áudio simulados
#     nframes = int(framerate * duracao_estimada)
#     audio_data = b''
#     for i in range(nframes):
#         t = float(i) / framerate
#         audio_data += struct.pack('h', int(amplitude * random.uniform(-1, 1)))
    
#     # Salvando o arquivo de áudio simulado
#     with wave.open(nome_arquivo, 'wb') as wf:
#         wf.setnchannels(1)
#         wf.setsampwidth(2)
#         wf.setframerate(framerate)
#         wf.writeframes(audio_data)
    
#     print(f"Áudio sintetizado salvo como {nome_arquivo}")
#     print(f"Duração estimada: {duracao_estimada:.2f} segundos")
    
#     return {
#         "arquivo": nome_arquivo,
#         "duracao": duracao_estimada,
#         "texto_original": texto,
#         "voz_usada": voz_clonada['clone_id']
#     }


# def gravar_amostra_voz(duracao=20, taxa_amostragem=44100, canais=1, formato=pyaudio.paInt16):
#     print("Preparando para gravar a amostra de voz...")
    
#     # Configurar PyAudio
#     p = pyaudio.PyAudio()
    
#     # Abrir stream
#     stream = p.open(format=formato,
#                     channels=canais,
#                     rate=taxa_amostragem,
#                     input=True,
#                     frames_per_buffer=1024)
    
#     print("Gravação iniciada. Fale por 20 segundos...")
    
#     frames = []
#     for i in range(0, int(taxa_amostragem / 1024 * duracao)):
#         data = stream.read(1024)
#         frames.append(data)
#         if i % 43 == 0:  # Aproximadamente a cada segundo
#             print(f"Gravando... {i // 43 + 1} segundos")
    
#     print("Gravação concluída.")
    
#     # Parar e fechar o stream
#     stream.stop_stream()
#     stream.close()
#     p.terminate()
    
#     # Salvar o arquivo de áudio
#     nome_arquivo = f"amostra_voz_{int(time.time())}.wav"
#     wf = wave.open(nome_arquivo, 'wb')
#     wf.setnchannels(canais)
#     wf.setsampwidth(p.get_sample_size(formato))
#     wf.setframerate(taxa_amostragem)
#     wf.writeframes(b''.join(frames))
#     wf.close()
    
#     print(f"Amostra de voz salva como {nome_arquivo}")
#     return nome_arquivo

# # Exemplo de uso
# # arquivo_amostra = gravar_amostra_voz()

# def clone_voice(voice_sample):
#     if len(voice_sample) < 20:
#         raise ValueError("A amostra de voz deve ter pelo menos 20 segundos.")
    
#     print("Iniciando o processo de clonagem de voz...")
#     time.sleep(2)  # Simulando processamento
    
#     # Simulando etapas de clonagem
#     print("Analisando características vocais...")
#     time.sleep(1)
#     print("Extraindo parâmetros de frequência...")
#     time.sleep(1)
#     print("Modelando entonação e ritmo...")
#     time.sleep(1)
#     print("Gerando modelo de voz sintética...")
#     time.sleep(2)
    
#     # Simulando qualidade do clone
#     quality = random.uniform(0.7, 0.99)
    
#     print(f"Clone de voz criado com sucesso! Qualidade estimada: {quality:.2%}")
    
#     return {
#         "clone_id": f"voice_clone_{int(time.time())}",
#         "quality": quality,
#         "sample_length": len(voice_sample),
#         "is_ready": True
#     }



# # arquivo_amostra = gravar_amostra_voz()

# # # Ler o arquivo de amostra (simplificado para este exemplo)
# # with open(arquivo_amostra, 'rb') as f:
# #     amostra_voz = f.read()

# # # Clonar a voz
# # resultado_clone = clone_voice(amostra_voz)
# # print(resultado_clone)

# # Exemplo de uso
# texto_exemplo = "Olá, este é um teste de síntese de voz com clone de voz."
# voz_clonada_exemplo = {
#     "clone_id": "voice_clone_1234567890",
#     "quality": 0.95,
#     "sample_length": 20,
#     "is_ready": True
# }

# resultado = texto_para_audio_clonado(texto_exemplo, voz_clonada_exemplo)
# print(resultado)

# # Exemplo de uso
# amostra_voz = "0" * 20  # Simulando uma amostra de voz de 20 segundos
# resultado = clone_voice(amostra_voz)
# print(resultado)

#RECONHECIMENTO DE VOZ
import speech_recognition as sr #importamos o modúlo

rec = sr.Recognizer() #instanciamos o modúlo do reconhecedor

with sr.Microphone() as fala: #chamos a gravação do microphone de fala
	frase = rec.listen(fala) #o metodo listen vai ouvir o que a gente falar e gravar na variavel frase
print(rec.recognize_google_cloud(frase, language='pt')) #transformando nossa fala em texto


# #TRANSFORMANDO TEXTO EM FALA
# import pyttsx # importamos o modúlo
# en = pyttsx.init() # meotodo init seleciona um ending de sintetização, no caso o espeak
# en.say("Hello, I am Ronan") # o metodo say para dizer o que queremos
# en.say('Nice to meet you') 
# en.runAndWait() # para ouvir o que foi escrito
# en.setProperty('voice', b'brazil') # mudamos a propriedade setando pelo id para pt-br, o lemento b diz que a string está em bytes
# en.say('Olá, tudo bem?')
# en.runAndWait()

# #TRANSFORMANDO TEXTO EM FALA - USANDO API DO GOOGLE
# from gtts import gTTS # importamos o modúlo gTTS
# voz = gTTS("Olá, tudo bem?", lang ="pt") # guardamos o nosso texto na variavel voz
# voz.save("voz.mp3") #salvamos com o comando save em mp3

# import subprocess as s #importamos o subprocess e renomeamos a s
# s.call(['MPC-HC', 'voz.mp3']) #com o comando call roda nosso comando de voz no player escolhido.