window.onload = function () {
    let signedIn = getToken() != null;
    displayView(signedIn);
};

function getToken() {
    return localStorage.getItem("token");
}

function displayView(signedIn) {
    if (signedIn) {
        document.getElementById("viewport").innerHTML = document.getElementById("profile_view").innerHTML;
        setupHomePanel();
        setupAccountPanel();

    } else {
        document.getElementById("viewport").innerHTML = document.getElementById("welcome_view").innerHTML;
        setupWelcomeView();
    }
}

function setupWelcomeView() {
    document.getElementById("login_form")?.setAttribute("onsubmit", "login(this); return false;");
    document.getElementById("signup_form")?.setAttribute("onsubmit", "signup(this); return false;");
    let repeatPasswordInput = document.getElementById("repeat_signup_password");
    repeatPasswordInput.oninput = function () { repeatPasswordInput.setCustomValidity(""); };
}

function setupHomePanel() {
    getUserInfo();
    document.getElementById("post_message_form")?.setAttribute("onsubmit", "postMessage(this); return false;");
    loadMessageWall();
    document.getElementById("message_wall_refresh_button").onclick = loadMessageWall;
}

function setupAccountPanel() {
    document.getElementById("tab_bar").childNodes?.forEach(tab => tab.onclick = function () {
        // Unselect all tabs and hide all panels.
        Array.from(document.getElementsByClassName("tab")).forEach(t => t.classList.remove("selected"));
        Array.from(document.getElementsByClassName("panel")).forEach(p => p.hidden = true);

        // Select the clicked tab and show its panel.
        tab.classList.add("selected");
        let panel_id = tab.getAttribute("data-panel");
        document.getElementById(panel_id).hidden = false;
    });
    document.getElementById("sign_out_button").onclick = signOut;
    document.getElementById("change_password_form")?.setAttribute("onsubmit", "changePassword(this); return false;");
    let repeatPasswordInput = document.getElementById("repeat_change_password_input");
    repeatPasswordInput.oninput = function () { repeatPasswordInput.setCustomValidity(""); };
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
        communicateToUser(res.message, "welcome_view");
    }
}

function signup(formData) {
    let repeatPasswordInput = document.getElementById("repeat_signup_password");

    if (validatePassword(formData.signup_password.value, formData.repeat_signup_password.value, repeatPasswordInput)) {
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
        } else {
            communicateToUser(res.message);
        }
    }
}

function validatePassword(psw1, psw2, pswInput) {
    // NOTE: pswInput need to have oninput setCustomValidity to empty string.
    if (psw1 != psw2) {
        pswInput.setCustomValidity("Passwords does not match.");
        return false;
    } else {
        return true;
    }
}

function communicateToUser(msg, msg_box_prefix) {
    let messageBoxText = document.getElementById(msg_box_prefix + "_message_box_text");
    let messageBox = document.getElementById(msg_box_prefix + "_message_box");
    messageBoxText.innerText = msg;

    // Animation from: https://codepen.io/mikeCky/pen/WWjLEq
    messageBox.classList.remove("hidden_animation");
    setTimeout(function () { messageBox.classList.add("hidden_animation"); }, 3000);
}

function signOut() {
    serverstub.signOut(getToken());
    localStorage.removeItem("token");
    displayView(false);
}

function changePassword(formData) {
    let psw = formData.change_password_input.value;
    let repeatPsw = formData.repeat_change_password_input.value;
    let repeatPasswordInput = document.getElementById("repeat_change_password_input");
    let form = document.getElementById("change_password_form");

    if (validatePassword(psw, repeatPsw, repeatPasswordInput)) {
        let res = serverstub.changePassword(getToken(), formData.current_password_input.value, psw);
        console.log(res);
        if (res.success) {
            form.reset();
        }
        communicateToUser(res.message, "account_panel");
    }
}

function getUserInfo() {
    let res = serverstub.getUserDataByToken(getToken());
    if (res.success) {
        document.getElementById("info_first_name").innerText = res.data.firstname;
        document.getElementById("info_family_name").innerText = res.data.familyname;
        document.getElementById("info_gender").innerText = res.data.gender;
        document.getElementById("info_country").innerText = res.data.country;
        document.getElementById("info_city").innerText = res.data.city;
        document.getElementById("info_email").innerText = res.data.email;
    } else {
        communicateToUser(res.message, "home_panel");
    }
}

function postMessage(formData) {
    let res = serverstub.postMessage(getToken(), formData.post_message_textarea.value, formData.to_email.value);
    if (res.success) {
        document.getElementById("post_message_form").reset();
    }
    communicateToUser(res.message, "home_panel");
}

function loadMessageWall() {
    let res = serverstub.getUserMessagesByToken(getToken());

    if (res.success) {
        let feed = document.getElementById("message_feed");
        let messages = "";
        res.data.forEach((msg) => messages += `<dt>${msg.writer}</dt><dd>${msg.content}</dd>`);
        feed.innerHTML = `<dl>${messages}</dl>`;
    } else {
        communicateToUser(res.message, "home_panel");
    }
}