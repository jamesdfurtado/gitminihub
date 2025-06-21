function togglePassword() {
    const pwd = document.getElementById("password");
    const btn = document.getElementById("toggle-btn");
    if (pwd.type === "password") {
        pwd.type = "text";
        btn.textContent = "Hide Password";
    } else {
        pwd.type = "password";
        btn.textContent = "See Password";
    }
}
