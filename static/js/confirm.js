function checkPasswords() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');

    if (password !== confirmPassword) {
        passwordInput.classList.add('is-invalid');
        confirmPasswordInput.classList.add('is-invalid');
        return false;
    } else {
        passwordInput.classList.remove('is-invalid');
        confirmPasswordInput.classList.remove('is-invalid');
        return true;
    }
}
document.getElementById('registration-form').addEventListener('submit', function(event){
    if(!checkPasswords()) {
        event.preventDefault();
    }
})