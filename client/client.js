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
    handle_login(formData.login_email.value, formData.login_password.value);
}

function handle_login(email, password) {
    console.log(email, password);
    document.getElementById("login_form").reset();
}

function signup(formData) {
    let repeatPasswordInput = document.getElementById("repeat_signup_password");

    if (formData.signup_password.value != formData.repeat_signup_password.value) {
        repeatPasswordInput.setCustomValidity("Passwords does not match.");
    } else {
        repeatPasswordInput.setCustomValidity("");
        let res = serverstub.signUp({
            email: formData.signup_email.value,
            password: formData.signup_password.value,
            firstname: formData.first_name.value,
            familyname: formData.family_name.value,
            gender: formData.gender.value,
            city: formData.city.value,
            country: formData.country.value,
        });
        if (res.success) {
            handle_login(formData.signup_email.value, formData.signup_password.value);
            document.getElementById("signup_form").reset();
        } else {
            communicateToUser(res.message);
        }
    }
    repeatPasswordInput.reportValidity();
}

function communicateToUser(msg) {
    let messageBoxText = document.getElementById("message_box_text");
    let messageBox = document.getElementById("message_box");
    messageBoxText.innerText = msg;

    // Animation from: https://codepen.io/mikeCky/pen/WWjLEq
    messageBox.classList.remove("hidden_animation");
    setTimeout(function () { messageBox.classList.add("hidden_animation"); }, 3000);
}