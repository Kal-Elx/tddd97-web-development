window.onload = function () {
    displayView(false);
    attachHandlers();
};

function displayView(signedIn) {
    let view = signedIn ? "profile_view" : "welcome_view";
    document.getElementById("viewport").innerHTML = document.getElementById(view).innerHTML;
};

function attachHandlers() {
    document.getElementById("login_form")?.setAttribute("onsubmit", "login(this); return false;");
    document.getElementById("signup_form")?.setAttribute("onsubmit", "signup(this); return false;");
    let repeatPasswordInput = document.getElementById("repeat_signup_password");
    if (repeatPasswordInput != null) {
        repeatPasswordInput.oninput = function () { repeatPasswordInput.setCustomValidity(""); };
    }
}

function login(formData) {
    // TODO: Login.
    document.getElementById("login_form").reset();
}

function signup(formData) {
    let repeatPasswordInput = document.getElementById("repeat_signup_password");

    if (formData.signup_password.value != formData.repeat_signup_password.value) {
        repeatPasswordInput.setCustomValidity("Passwords does not match.");
    } else {
        repeatPasswordInput.setCustomValidity("");
        // TODO: Sign up.
        document.getElementById("signup_form").reset();
    }
    repeatPasswordInput.reportValidity();
}
