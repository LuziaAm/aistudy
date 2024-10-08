document.addEventListener('DOMContentLoaded', function() {
    const gravarBtn = document.getElementById('gravar');
    const pararBtn = document.getElementById('parar');
    const statusEl = document.getElementById('status');
    const downloadContainer = document.getElementById('download-container');
    const downloadBtn = document.getElementById('download');
    const discardBtn = document.getElementById('discard');
    const filenameEl = document.getElementById('filename');
    const textInput = document.getElementById('textInput');

    let currentFilename = null;

    gravarBtn.addEventListener('click', function() {
        fetch('/iniciar_gravacao', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            statusEl.textContent = data.message;
            gravarBtn.style.display = 'none';
            pararBtn.style.display = 'inline-block';
            downloadContainer.style.display = 'none';
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
            if (data.filename) {
                currentFilename = data.filename;
                filenameEl.textContent = currentFilename;
                downloadContainer.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            statusEl.textContent = 'Erro ao parar gravação';
        });
    });

    downloadBtn.addEventListener('click', function() {
        if (currentFilename) {
            window.location.href = `/download/${currentFilename}`;
            downloadContainer.style.display = 'none';
        }
    });

    discardBtn.addEventListener('click', function() {
        if (currentFilename) {
            fetch(`/descartar/${currentFilename}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                statusEl.textContent = data.message;
                downloadContainer.style.display = 'none';
            })
            .catch(error => {
                console.error('Erro:', error);
                statusEl.textContent = 'Erro ao descartar arquivo';
            });
        }
    });
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        // Adiciona o texto do textInput ao formData
        formData.append('text', textInput.value);
        
        fetch('/process', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            outputAudio.src = data.output_audio;
            downloadAudio.href = data.download_url;
            textInput.value;
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro no processamento: ' + error.message);
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
        $('#voiceSampleStatus').text('Gravando amostra de voz por 20 segundos. Comece a falar...');
        $('#recordVoiceSample').prop('disabled', true);
        
        $.post('/record_voice_sample', function(data) {
            setTimeout(function() {
                $('#voiceSampleStatus').text('Amostra de voz gravada com sucesso');
                $('#voice_sample_recorded').val('true');
                $('#recordVoiceSample').prop('disabled', false);
            }, 20000); // 20 segundos
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

let translationText = '';

document.getElementById("translateButton").addEventListener("click", function() {
    const text = document.getElementById("text").value;
    const formData = new FormData();
    formData.append("text", text);

    fetch("/processtxt", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("message").textContent = data.error;
        } else {
            document.getElementById("translationResult").textContent = "Tradução: " + data.translation;
            translationText = data.translation;
            document.getElementById("downloadButton").disabled = false; // Habilitar o botão de download
        }
    })
    .catch(error => console.error("Erro:", error));
});

document.getElementById("downloadButton").addEventListener("click", function() {
    const formData = new FormData();
    formData.append("translation", translationText);

    fetch("/download_audio", {
        method: "POST",
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "translation.mp3";
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => console.error("Erro:", error));
});
