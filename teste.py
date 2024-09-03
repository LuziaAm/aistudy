import speech_recognition as sr
from pydub import AudioSegment
from googletrans import Translator
import os
import torch
from gtts import gTTS
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice
import argparse

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
        tts = gTTS(text=texto, lang=idioma)
        tts.save(caminho_saida)
        print(f"Áudio gerado: {caminho_saida}")
    except Exception as e:
        print(f"Erro ao gerar áudio com gTTS: {e}")

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

def record_voice_sample(output_file, duration=60):
    """Grava uma amostra de voz do usuário."""
    try:
        recognizer = sr.Recognizer()
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

def process_audio(audio_file, source_language, target_language, output_audio, use_voice_sample):
    """Processa o áudio: transcrição, tradução e geração de novo áudio."""
    # Transcrição
    print("\nTranscrevendo o áudio...")
    transcribed_text = transcribe_audio(audio_file, source_language)
    print("\nTranscrição original:")
    print(transcribed_text)
    
    # Tradução
    if source_language != target_language:
        print("\nTraduzindo o texto...")
        translated_text = translate_text(transcribed_text, target_language)
        if translated_text:
            print("\nTexto traduzido:")
            print(translated_text)
            
            # Gerando áudio
            if use_voice_sample:
                voice_sample = "voice_sample.wav"
                if record_voice_sample(voice_sample):
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

def main():
    parser = argparse.ArgumentParser(description="Transcrição, tradução e síntese de fala de áudio.")
    parser.add_argument("--audio", required=True, help="Caminho do arquivo de áudio de entrada")
    parser.add_argument("--source-lang", default="pt-BR", help="Código do idioma do áudio de origem")
    parser.add_argument("--target-lang", default="en", help="Código do idioma para tradução")
    parser.add_argument("--output", default="audio_traduzido.wav", help="Caminho para salvar o arquivo de áudio traduzido")
    parser.add_argument("--use-voice-sample", action="store_true", help="Usar amostra de voz personalizada")
    
    args = parser.parse_args()
    
    process_audio(args.audio, args.source_lang, args.target_lang, args.output, args.use_voice_sample)

if __name__ == "__main__":
    # use para executar: python teste.py --audio gravacao.wav --source-lang pt-BR --target-lang en --output translated.wav --use-voice-sample
    main()