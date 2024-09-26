document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const messageDiv = document.getElementById('message');
    
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `email=${encodeURIComponent(email)}`
    })
    .then(response => {
        if (response.redirected) {
            // Se o servidor redirecionar, siga o redirecionamento
            window.location.href = response.url;
        } else {
            // Se não houver redirecionamento, trate como erro
            throw new Error('Erro no servidor');
        }
    })
    .then(() => {
        messageDiv.textContent = 'Código enviado com sucesso! Redirecionando...';
        messageDiv.className = 'success';
    })
    .catch(error => {
        messageDiv.textContent = 'Erro ao enviar o código. Por favor, tente novamente.';
        messageDiv.className = 'error';
        console.error('Erro:', error);
    });
});