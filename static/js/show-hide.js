// Função para mostrar ou esconder a senha do input
function togglePassword() {
  var passwordInput = document.getElementById('password');
  var toggle = document.querySelector('.show-password');
  if (passwordInput.type === 'password') {
      passwordInput.type = 'text';
      toggle.textContent = 'Esconder';
  } else {
      passwordInput.type = 'password';
      toggle.textContent = 'Mostrar';
  }
}