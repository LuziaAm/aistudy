import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment

def transcrever_audio(caminho_audio):
    reconhecedor = sr.Recognizer()
    with sr.AudioFile(caminho_audio) as fonte:
        audio = reconhecedor.record(fonte)
    try:
        texto = reconhecedor.recognize_google(audio, language='pt-BR')
        print("Transcrição: " + texto)
        return texto
    except sr.UnknownValueError:
        print("Não foi possível entender o áudio")
        return None
    except sr.RequestError as e:
        print("Erro ao solicitar resultados; {0}".format(e))
        return None

def traduzir_texto(texto, idioma_destino):
    tradutor = Translator()
    traducao = tradutor.translate(texto, dest=idioma_destino)
    print("Tradução: " + traducao.text)
    return traducao.text

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
    texto_traduzido = traduzir_texto(texto_transcrito, idioma_destino)

    # Gerar novo áudio com a tradução
    gerar_audio(texto_traduzido, caminho_saida_audio, idioma=idioma_destino)

if __name__ == "__main__":
    main()
