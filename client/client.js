window.onload = function () {
    let signedIn = localStorage.getItem("token") != null;
    displayView(signedIn);
};

function displayView(signedIn) {
    if (signedIn) {
        document.getElementById("viewport").innerHTML = document.getElementById("profile_view").innerHTML;

        // Attach handlers.
        document.getElementById("tab_bar").childNodes?.forEach(tab => tab.onclick = function () {
            // Unselect all tabs and hide all panels.
            Array.from(document.getElementsByClassName("tab")).forEach(t => t.classList.remove("selected"));
            Array.from(document.getElementsByClassName("panel")).forEach(p => p.hidden = true);

            // Select the clicked tab and show its panel.
            tab.classList.add("selected");
            let panel_id = tab.getAttribute("data-panel");
            document.getElementById(panel_id).hidden = false;
        });

    } else {
        document.getElementById("viewport").innerHTML = document.getElementById("welcome_view").innerHTML;

        // Attach handlers.
        document.getElementById("login_form")?.setAttribute("onsubmit", "login(this); return false;");
        document.getElementById("signup_form")?.setAttribute("onsubmit", "signup(this); return false;");
        document.getElementById("repeat_signup_password").oninput = function () { repeatPasswordInput.setCustomValidity(""); };
    }
}

function login(formData) {
    handle_login(formData.login_email.value, formData.login_password.value);
}

function handle_login(email, password) {
    let res = serverstub.signIn(email, password);
    if (res.success) {
        let token = res.data;
        localStorage.setItem("token", token);
        document.getElementById("login_form").reset();
        displayView(true);
    } else {
        communicateToUser(res.message);
    }
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