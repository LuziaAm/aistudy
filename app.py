from flask import Flask, request, jsonify, render_template, send_from_directory, url_for, send_file
import os
import traceback
import logging
from werkzeug.utils import secure_filename
from transcricao_audio import record_input_audio, process_audio, record_voice_sample, gerar_audio
import threading
import pyaudio
import wave
import uuid


app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

is_recording = False
frames = []
current_audio_file = None

@app.route('/')
def index():
    return render_template('index.html')

def audio_recording():
    global is_recording, frames
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    while is_recording:
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/process', methods=['POST'])
def process():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            source_language = request.form.get('source_language', 'pt-BR')
            target_language = request.form.get('target_language', 'en')
            output_audio = 'audio_traduzido.mp3'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_audio)
            
            use_voice_sample = request.form.get('use_voice_sample') == 'true'
            voice_sample_recorded = request.form.get('voice_sample_recorded') == 'true'

            voice_sample_path = None
            if use_voice_sample and voice_sample_recorded:
                voice_sample_path = os.path.join(app.config['UPLOAD_FOLDER'], 'voice_sample.wav')
                if not os.path.exists(voice_sample_path):
                    app.logger.warning("Voice sample file not found. Falling back to gTTS.")
                    use_voice_sample = False
                    voice_sample_path = None

            app.logger.info(f"Processing audio: {filepath}")
            app.logger.info(f"Source language: {source_language}")
            app.logger.info(f"Target language: {target_language}")
            app.logger.info(f"Use voice sample: {use_voice_sample}")
            app.logger.info(f"Voice sample recorded: {voice_sample_recorded}")
            app.logger.info(f"Voice sample path: {voice_sample_path}")

            result = process_audio(filepath, source_language, target_language, output_path, use_voice_sample, voice_sample_path)

            # Se não estiver usando amostra de voz, gera áudio com gTTS
            if not use_voice_sample:
                app.logger.info("Using gTTS for audio generation")
                gerar_audio(result['translation'], output_path, target_language)

            download_url = url_for('uploaded_file', filename=output_audio)
            
            return jsonify({
                'message': 'Processamento concluído',
                'transcription': result['transcription'],
                'translation': result['translation'],
                'output_audio': f'/uploads/{output_audio}',
                'download_url': download_url
            })
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        app.logger.error(f"Error in /process: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'An internal error occurred'}), 500

@app.route('/start_recording', methods=['POST'])
def start_recording():
    try:
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], "user_voice.wav")
        
        # Inicia a gravação em uma thread separada
        threading.Thread(target=record_input_audio, args=(output_file,)).start()
        
        return jsonify({'message': 'Gravação iniciada'}), 200
    except Exception as e:
        app.logger.error(f"Error in /start_recording: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'An internal error occurred'}), 500

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    try:
        # Aqui você precisaria implementar uma maneira de parar a gravação
        # Por exemplo, definindo uma variável global ou usando um mecanismo de sinalização
        
        return jsonify({'message': 'Gravação finalizada', 'file': 'user_voice.wav'}), 200
    except Exception as e:
        app.logger.error(f"Error in /stop_recording: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'An internal error occurred'}), 500
    
@app.route('/record_voice_sample', methods=['POST'])
def record_voice():
    try:
        voice_sample_path = os.path.join(app.config['UPLOAD_FOLDER'], 'voice_sample.wav')
        success = record_voice_sample(voice_sample_path)
        if success:
            return jsonify({'message': 'Amostra de voz gravada com sucesso'}), 200
        else:
            return jsonify({'error': 'Falha ao gravar amostra de voz'}), 500
    except Exception as e:
        app.logger.error(f"Error in /record_voice_sample: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'An internal error occurred'}), 500

@app.route('/record', methods=['POST'])
def record():
    try:
        audio_file = record_input_audio(os.path.join(app.config['UPLOAD_FOLDER'], "audioInput.wav"))
        if not audio_file:
            return jsonify({'error': 'Falha ao gravar o áudio de entrada'}), 500
        return jsonify({'message': 'Áudio gravado com sucesso', 'file': audio_file})
    except Exception as e:
        app.logger.error(f"Error in /record: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'An internal error occurred'}), 500

@app.route('/iniciar_gravacao', methods=['POST'])
def iniciar_gravacao():
    global is_recording
    if not is_recording:
        is_recording = True
        threading.Thread(target=audio_recording).start()
        return jsonify({"status": "success", "message": "Gravação iniciada"})
    else:
        return jsonify({"status": "error", "message": "Gravação já em andamento"})

@app.route('/parar_gravacao', methods=['POST'])
def parar_gravacao():
    global is_recording, frames, current_audio_file
    if is_recording:
        is_recording = False
        # Espera um pouco para garantir que a thread de gravação tenha terminado
        threading.Event().wait(1)
        
        # Gera um nome de arquivo único
        filename = f"gravacao_{uuid.uuid4().hex[:8]}.wav"
        WAVE_OUTPUT_FILENAME = os.path.join(app.static_folder, filename)
        
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        current_audio_file = filename
        
        return jsonify({"status": "success", "message": "Gravação finalizada", "filename": filename})
    else:
        return jsonify({"status": "error", "message": "Nenhuma gravação em andamento"})
    
@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.static_folder, filename), as_attachment=True)

@app.route('/descartar/<filename>', methods=['POST'])
def descartar_arquivo(filename):
    file_path = os.path.join(app.static_folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"status": "success", "message": "Arquivo descartado"})
    else:
        return jsonify({"status": "error", "message": "Arquivo não encontrado"})
    
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)