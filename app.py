from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
import os
import traceback
import logging
from werkzeug.utils import secure_filename
from transcricao_audio import record_input_audio, process_audio, record_voice_sample, gerar_audio

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)