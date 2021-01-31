window.onload = function () {
    let signedIn = getToken() != null;
    displayView(signedIn);
};

function getToken() {
    return localStorage.getItem("token");
}

function getUserEmail(panel) {
    return document.getElementById(panel + "_info_email").textContent;
}

function displayView(signedIn) {
    if (signedIn) {
        document.getElementById("viewport").innerHTML = document.getElementById("profile_view").innerHTML;
        setupHomePanel();
        setupBrowsePanel();
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
    document.getElementById("home_panel_post_message_form")?.setAttribute("onsubmit", "postMessage(this); return false;");
    loadHomePanelMessageWall();
    document.getElementById("home_message_wall_refresh_button").onclick = loadHomePanelMessageWall;
}

function setupBrowsePanel() {
    document.getElementById("search_user_form")?.setAttribute("onsubmit", "searchUser(this); return false;");
    document.getElementById("browse_panel_post_message_form")?.setAttribute("onsubmit", "postMessage(this, true); return false;");
    document.getElementById("browse_message_wall_refresh_button").onclick = function () {
        loadBrowsePanelMessageWall(getUserEmail("browse_panel"));
    };
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
        populateUserInfo(res.data, "home_panel");
    } else {
        communicateToUser(res.message, "home_panel");
    }
}

function populateUserInfo(data, panel) {
    let prefix = panel + "_";
    document.getElementById(`${prefix}info_first_name`).innerText = data.firstname;
    document.getElementById(`${prefix}info_family_name`).innerText = data.familyname;
    document.getElementById(`${prefix}info_gender`).innerText = data.gender;
    document.getElementById(`${prefix}info_country`).innerText = data.country;
    document.getElementById(`${prefix}info_city`).innerText = data.city;
    document.getElementById(`${prefix}info_email`).innerText = data.email;
}

function postMessage(formData, postToFoundUser = false) {
    let panel = postToFoundUser ? "browse_panel" : "home_panel";
    let toEmail = getUserEmail(panel);
    let res = serverstub.postMessage(getToken(), formData.post_message_textarea.value, toEmail);
    console.log(res);
    if (res.success) {
        document.getElementById(panel + "_post_message_form").reset();
    }
    communicateToUser(res.message, panel);
}

function loadHomePanelMessageWall() {
    let res = serverstub.getUserMessagesByToken(getToken());

    if (res.success) {
        populateMessageWall("home_panel", res.data);
    } else {
        communicateToUser(res.message, "home_panel");
    }
}

function populateMessageWall(panel, data) {
    let feed = document.getElementById(panel + "_message_feed");
    let messages = "";
    data.forEach((msg) => messages += `<dt>${msg.writer}</dt><dd>${msg.content}</dd>`);
    feed.innerHTML = `<dl>${messages}</dl>`;
}

function searchUser(formData) {
    let email = formData.user_email.value;
    let res = serverstub.getUserDataByEmail(getToken(), email);

    if (res.success) {
        document.getElementById("search_user_form").reset();
        populateUserInfo(res.data, "browse_panel");
        loadBrowsePanelMessageWall(email);
        toggleFoundUserInfo(true);
    } else {
        communicateToUser(res.message, "browse_panel");
        toggleFoundUserInfo(false);
    }
}

function loadBrowsePanelMessageWall(email) {
    let res = serverstub.getUserMessagesByEmail(getToken(), email);

    if (res.success) {
        populateMessageWall("browse_panel", res.data);
    } else {
        communicateToUser(res.message, "browse_panel");
    }
}

function toggleFoundUserInfo(show) {
    let info = document.getElementById("user_info_group");
    if (show) {
        info.classList.remove("hidden_animation");
    } else {
        info.classList.add("hidden_animation");
    }
}
