import speech_recognition as sr
from pydub import AudioSegment
from googletrans import Translator
import os
import torch
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice

def convert_to_wav(audio_file):
    """Converte o arquivo de áudio para WAV se necessário."""
    name, ext = os.path.splitext(audio_file)
    if ext.lower() != '.wav':
        audio = AudioSegment.from_file(audio_file)
        wav_file = f"{name}.wav"
        audio.export(wav_file, format="wav")
        return wav_file
    return audio_file

def transcribe_audio(audio_file, language='pt-BR'):
    """Transcreve o arquivo de áudio para texto."""
    recognizer = sr.Recognizer()
    
    wav_file = convert_to_wav(audio_file)
    
    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)
        
    try:
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition não conseguiu entender o áudio"
    except sr.RequestError as e:
        return f"Não foi possível requisitar resultados do Google Speech Recognition; {e}"

def translate_text(text, target_language):
    """Traduz o texto para o idioma alvo."""
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

def clone_voice_and_generate_speech(text, voice_sample, output_file):
    """Clona a voz do usuário e gera áudio com o texto fornecido."""
    tts = TextToSpeech()
    voice_samples, conditioning_latents = load_voice(voice_sample)
    gen = tts.tts_with_preset(text, voice_samples=voice_samples, conditioning_latents=conditioning_latents, preset="fast")
    tts.save_audio(gen, output_file)
    print(f"Áudio gerado e salvo como {output_file}")

def record_voice_sample(output_file, duration=60):
    """Grava uma amostra de voz do usuário."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Gravando amostra de voz por {duration} segundos. Comece a falar...")
        audio = recognizer.record(source, duration=duration)
    
    with open(output_file, "wb") as f:
        f.write(audio.get_wav_data())
    print(f"Amostra de voz gravada e salva como {output_file}")

def main():
    audio_file = input("Digite o caminho do arquivo de áudio: ")
    source_language = input("Digite o código do idioma do áudio (ex: 'pt-BR' para português do Brasil): ")
    target_language = input("Digite o código do idioma para tradução (ex: 'en' para inglês): ")
    output_audio = input("Digite o caminho para salvar o arquivo de áudio traduzido: ")
    
    if not source_language:
        source_language = 'pt-BR'
    if not target_language:
        target_language = 'en'
    if not output_audio:
        output_audio = "audio_traduzido.wav"
    
    # Gravar amostra de voz do usuário
    voice_sample = "voice_sample.wav"
    record_voice_sample(voice_sample)
    
    # Transcrição
    print("\nTranscrevendo o áudio...")
    transcribed_text = transcribe_audio(audio_file, source_language)
    print("\nTranscrição original:")
    print(transcribed_text)
    
    # Tradução
    if source_language != target_language:
        print("\nTraduzindo o texto...")
        translated_text = translate_text(transcribed_text, target_language)
        print("\nTexto traduzido:")
        print(translated_text)
        
        # Clonando voz e gerando áudio
        print("\nGerando áudio com voz clonada...")
        clone_voice_and_generate_speech(translated_text, voice_sample, output_audio)
    else:
        print("\nOs idiomas de origem e destino são os mesmos. Nenhuma tradução necessária.")

if __name__ == "__main__":
    main()