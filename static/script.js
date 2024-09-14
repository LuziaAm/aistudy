document.addEventListener('DOMContentLoaded', function() {
    const gravarBtn = document.getElementById('gravar');
    const pararBtn = document.getElementById('parar');
    const statusEl = document.getElementById('status');

    gravarBtn.addEventListener('click', function() {
        fetch('/iniciar_gravacao', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            statusEl.textContent = data.message;
            gravarBtn.style.display = 'none';
            pararBtn.style.display = 'inline-block';
        })
        .catch(error => {
            console.error('Erro:', error);
            statusEl.textContent = 'Erro ao iniciar gravação';
        });
    });

    pararBtn.addEventListener('click', function() {
        fetch('/parar_gravacao', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            statusEl.textContent = data.message;
            gravarBtn.style.display = 'inline-block';
            pararBtn.style.display = 'none';
        })
        .catch(error => {
            console.error('Erro:', error);
            statusEl.textContent = 'Erro ao parar gravação';
        });
    });
});
$(document).ready(function() {
    $('#use_voice_sample').change(function() {
        $('#voiceSampleSection').toggle(this.checked);
        if (!this.checked) {
            $('#voice_sample_recorded').val('false');
            $('#voiceSampleStatus').text('');
        }
    });

    $('#recordVoiceSample').click(function() {
        $('#voiceSampleStatus').text('Gravando amostra de voz por 10 segundos. Comece a falar...');
        $('#recordVoiceSample').prop('disabled', true);
        
        $.post('/record_voice_sample', function(data) {
            setTimeout(function() {
                $('#voiceSampleStatus').text('Amostra de voz gravada com sucesso');
                $('#voice_sample_recorded').val('true');
                $('#recordVoiceSample').prop('disabled', false);
            }, 10000); // 10 segundos
        }).fail(function(error) {
            $('#voiceSampleStatus').text('Erro ao gravar amostra de voz: ' + error.responseJSON.error);
            $('#voice_sample_recorded').val('false');
            $('#recordVoiceSample').prop('disabled', false);
        });
    });

    $('#recordButton').click(function() {
        $.post('/record', function(data) {
            $('#recordStatus').text('Áudio gravado: ' + data.file);
        }).fail(function(error) {
            $('#recordStatus').text('Erro ao gravar: ' + error.responseJSON.error);
        });
    });

    $('#uploadForm').submit(function(e) {
        e.preventDefault();
        var formData = new FormData(this);
        
        formData.set('use_voice_sample', $('#use_voice_sample').is(':checked'));
        
        $.ajax({
            url: '/process',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(data) {
                $('#transcription').text(data.transcription);
                $('#translation').text(data.translation);
                $('#outputAudio').attr('src', data.output_audio);
                $('#downloadAudio').attr('href', data.download_url);
                $('#result').show();
            },
            error: function(error) {
                alert('Erro no processamento: ' + error.responseJSON.error);
            }
        });
    });
});