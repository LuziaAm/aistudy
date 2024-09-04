import speech_recognition as sr
from pydub import AudioSegment
from googletrans import Translator
import os
import torch
from gtts import gTTS
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice
import threading
import wave
import pyaudio

def record_voice_sample(output_file, duration=10):
    """Grava uma amostra de voz do usuário."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print(f"Gravando amostra de voz por {duration} segundos. Comece a falar...")
            audio = recognizer.record(source, duration=duration)
        
        with open(output_file, "wb") as f:
            f.write(audio.get_wav_data())
        print(f"Amostra de voz gravada e salva como {output_file}")
        return True
    except Exception as e:
        print(f"Erro ao gravar amostra de voz: {e}")
        return False


def process_audio(audio_file, source_language, target_language, output_audio, use_voice_sample, voice_sample_path=None):
    """Processa o áudio: transcrição, tradução e geração de novo áudio."""
    result = {
        'transcription': '',
        'translation': '',
        'output_audio': output_audio
    }

    # Transcrição
    print("\nTranscrevendo o áudio...")
    transcribed_text = transcribe_audio(audio_file, source_language)
    result['transcription'] = transcribed_text
    print("\nTranscrição original:")
    print(transcribed_text)
    
    # Tradução
    if source_language != target_language:
        print("\nTraduzindo o texto...")
        translated_text = translate_text(transcribed_text, target_language)
        if translated_text:
            result['translation'] = translated_text
            print("\nTexto traduzido:")
            print(translated_text)
            
            # Gerando áudio
            if use_voice_sample and voice_sample_path:
                print("\nGerando áudio com voz clonada...")
                clone_voice_and_generate_speech(translated_text, voice_sample_path, output_audio)
            else:
                print("Usando voz padrão do sistema...")
                gerar_audio(translated_text, output_audio, target_language)
        else:
            print("Falha na tradução. O áudio não será gerado.")
    else:
        print("\nOs idiomas de origem e destino são os mesmos. Nenhuma tradução necessária.")
    
    return result

def record_input_audio(output_file="audioInput.wav"):
    """Grava o áudio de entrada do usuário controlado por Enter."""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    frames = []

    def callback(in_data, frame_count, time_info, status):
        frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    print("Pressione Enter para iniciar a gravação...")
    input()
    print("Gravação iniciada. Pressione Enter novamente para parar.")
    
    stream.start_stream()
    
    input()  # Espera o usuário pressionar Enter novamente
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    print("Gravação finalizada.")

    # Salva o arquivo de áudio
    wf = wave.open(output_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"Áudio de entrada gravado e salvo como {output_file}")
    return output_file

def convert_to_wav(audio_file):
    """Converte o arquivo de áudio para WAV se necessário."""
    name, ext = os.path.splitext(audio_file)
    if ext.lower() != '.wav':
        try:
            audio = AudioSegment.from_file(audio_file)
            wav_file = f"{name}.wav"
            audio.export(wav_file, format="wav")
            return wav_file
        except Exception as e:
            print(f"Erro ao converter arquivo para WAV: {e}")
            return None
    return audio_file

def transcribe_audio(audio_file, language='pt-BR'):
    """Transcreve o arquivo de áudio para texto."""
    recognizer = sr.Recognizer()
    
    wav_file = convert_to_wav(audio_file)
    if not wav_file:
        return "Erro na conversão do arquivo de áudio."
    
    try:
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
        
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition não conseguiu entender o áudio"
    except sr.RequestError as e:
        return f"Não foi possível requisitar resultados do Google Speech Recognition; {e}"
    except Exception as e:
        return f"Erro na transcrição: {e}"

def translate_text(text, target_language):
    """Traduz o texto para o idioma alvo."""
    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        print(f"Erro na tradução: {e}")
        return None

def gerar_audio(texto, caminho_saida, idioma):
    """Gera áudio usando gTTS."""
    try:
        # Verifica se o caminho fornecido é um diretório
        if os.path.isdir(caminho_saida):
            # Se for um diretório, cria um nome de arquivo padrão
            caminho_saida = os.path.join(caminho_saida, "audio_gerado.mp3")
        
        # Garante que o diretório pai existe
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        
        tts = gTTS(text=texto, lang=idioma)
        tts.save(caminho_saida)
        print(f"Áudio gerado: {caminho_saida}")
    except Exception as e:
        print(f"Erro ao gerar áudio com gTTS: {e}")
        print("Tentando salvar no diretório atual...")
        try:
            # Tenta salvar no diretório atual com um nome padrão
            caminho_saida = "audio_gerado.mp3"
            tts = gTTS(text=texto, lang=idioma)
            tts.save(caminho_saida)
            print(f"Áudio gerado: {caminho_saida}")
        except Exception as e:
            print(f"Falha ao gerar áudio: {e}")

def clone_voice_and_generate_speech(text, voice_sample, output_file):
    """Clona a voz do usuário e gera áudio com o texto fornecido."""
    try:
        tts = TextToSpeech()
        voice_samples, conditioning_latents = load_voice(voice_sample)
        gen = tts.tts_with_preset(text, voice_samples=voice_samples, conditioning_latents=conditioning_latents, preset="fast")
        tts.save_audio(gen, output_file)
        print(f"Áudio gerado e salvo como {output_file}")
    except Exception as e:
        print(f"Erro ao gerar áudio com voz clonada: {e}")
        print("Usando voz padrão do sistema...")
        gerar_audio(text, output_file, 'pt')

def process_audio(audio_file, source_language, target_language, output_audio, use_voice_sample, voice_sample_path):
    """Processa o áudio: transcrição, tradução e geração de novo áudio."""
    result = {
        'transcription': '',
        'translation': '',
        'output_audio': output_audio
    }

    # Transcrição
    print("\nTranscrevendo o áudio...")
    transcribed_text = transcribe_audio(audio_file, source_language)
    result['transcription'] = transcribed_text
    print("\nTranscrição original:")
    print(transcribed_text)
    
    # Tradução
    if source_language != target_language:
        print("\nTraduzindo o texto...")
        translated_text = translate_text(transcribed_text, target_language)
        if translated_text:
            result['translation'] = translated_text
            print("\nTexto traduzido:")
            print(translated_text)
            
            # Gerando áudio
            if use_voice_sample:
                voice_sample = "voice_sample.wav"
                if record_input_audio(voice_sample):
                    print("\nGerando áudio com voz clonada...")
                    clone_voice_and_generate_speech(translated_text, voice_sample, output_audio)
                else:
                    print("Usando voz padrão do sistema...")
                    gerar_audio(translated_text, output_audio, target_language)
            else:
                gerar_audio(translated_text, output_audio, target_language)
        else:
            print("Falha na tradução. O áudio não será gerado.")
    else:
        print("\nOs idiomas de origem e destino são os mesmos. Nenhuma tradução necessária.")
    
    return result

def main():
    print("Bem-vindo ao sistema de transcrição, tradução e síntese de fala de áudio.")
    
    # Grava o áudio de entrada
    audio_file = record_input_audio("audioInput.wav")
    if not audio_file:
        print("Falha ao gravar o áudio de entrada. Encerrando o programa.")
        return

    source_language = input("Digite o código do idioma do áudio de origem (ex: 'pt-BR' para português do Brasil): ") or "pt-BR"
    target_language = input("Digite o código do idioma para tradução (ex: 'en' para inglês): ") or "en"
    
    while True:
        output_audio = input("Digite o caminho para salvar o arquivo de áudio traduzido (incluindo o nome do arquivo): ") or "audio_traduzido.mp3"
        if os.path.isdir(output_audio):
            print("O caminho fornecido é um diretório. Por favor, inclua o nome do arquivo.")
        else:
            break
    
    use_voice_sample = input("Deseja usar uma amostra de voz personalizada para o áudio de saída? (s/n): ").lower() == 's'
    
    process_audio(audio_file, source_language, target_language, output_audio, use_voice_sample)

if __name__ == "__main__":
    main()