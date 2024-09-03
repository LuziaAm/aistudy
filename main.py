import speech_recognition as sr
from googletrans import Translator
# from translate import Translator
from gtts import gTTS
from pydub import AudioSegment
import whisper
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice


def transcrever_audio(caminho_audio):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(caminho_audio)
        return result["text"]
    except sr.UnknownValueError:
        print("Não foi possível entender o áudio")
        return None
    except sr.RequestError as e:
        print("Erro ao solicitar resultados; {0}".format(e))
        return None

def traduzir_texto(texto, idioma_destino):
    tradutor = Translator()
    traducao = tradutor.translate(texto, dest=idioma_destino)
    return traducao

def gerar_audio(texto, caminho_saida, idioma='en'):
    tts = gTTS(text=texto, lang=idioma)
    tts.save(caminho_saida)
    print("Áudio gerado: " + caminho_saida)

def converter_audio_para_wav(caminho_audio):
    audio = AudioSegment.from_file(caminho_audio)
    caminho_wav = caminho_audio.replace('.mp3', '.wav')
    audio.export(caminho_wav, format="wav")
    return caminho_wav

def main():
    caminho_audio = "gravacao.wav"  # Caminho do arquivo de áudio de entrada
    idioma_destino = "en"  # Idioma para tradução (por exemplo, 'en' para inglês)
    caminho_saida_audio = "traducao.mp3"  # Caminho do arquivo de áudio de saída

    # Converte o áudio para wav se necessário
    if caminho_audio.endswith('.mp3'):
        caminho_audio = converter_audio_para_wav(caminho_audio)
    # Transcrever o áudio
    texto_transcrito = transcrever_audio(caminho_audio)
    if texto_transcrito is None:
        return
    # Traduzir o texto
    texto_traduzido = traduzir_texto(texto_transcrito, idioma_destino).text
    # Gerar novo áudio com a tradução
    gerar_audio(texto_traduzido, caminho_saida_audio, idioma=idioma_destino)

if __name__ == "__main__":
    main()
