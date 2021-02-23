window.onload = function () {
    let signedIn = getToken() != null;
    displayView(signedIn);
};

/**
 * Makes a request to the server.
 * @param {string} url The url to send the request.
 * @param {string} method The method in caps.
 * @param {object} data The data that is going to be the JSON body of the request.
 * @param {function(object)} onSuccess What to do if the request was succesful.
 * @param {function(object)} onError  What to do if the request failed.
 */
function makeRequest(url, method, data, onSuccess, onError, authorization = false) {
    let r = new XMLHttpRequest();
    r.onreadystatechange = function () {
        if (this.readyState == 4) {
            let res = JSON.parse(this.responseText)
            if (this.status == 200) {
                onSuccess(res.data)
            } else {
                onError(this.status)
            }
        }
    }
    r.open(method, url, true);
    r.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    if (authorization) {
        r.setRequestHeader("authorization", getToken());
    }
    r.send(JSON.stringify(data));
}

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
        setupSession();

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
    let chartCtx = document.getElementById("live_data_chart");
    chart = new Chart(chartCtx, {
        type: 'bar',
        data: {
            labels: ['Signed in users', 'Sent messages', 'Nationalities on Twidder'],
            datasets: [{
                label: 'Twidder Statistics',
                data: [0, 0, 0,],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        maxTicksLimit: 6
                    }
                }]
            }
        }
    });
}

function login(formData) {
    handle_login(formData.login_email.value, formData.login_password.value);
}

function handle_login(email, password) {
    makeRequest("/sign_in", "POST", { 'email': email, 'password': password },
        /* onSuccess */
        function (data) {
            let token = data.token;
            localStorage.setItem("token", token);
            document.getElementById("login_form").reset();
            displayView(true);
        },
        function (code) {
            switch (code) {
                case 401:
                    msg = "Wrong username or password."
                    break;
                case 400:
                default:
                    msg = "Application error, try again."
            }
            communicateToUser(msg, "welcome_view");
        })
}

function signup(formData) {
    let repeatPasswordInput = document.getElementById("repeat_signup_password");

    if (validatePassword(formData.signup_password.value, formData.repeat_signup_password.value, repeatPasswordInput)) {
        repeatPasswordInput.setCustomValidity("");

        makeRequest("/sign_up", "post",
            {
                email: formData.signup_email.value,
                password: formData.signup_password.value,
                firstname: formData.first_name.value,
                familyname: formData.family_name.value,
                gender: formData.gender.value,
                city: formData.city.value,
                country: formData.country.value,
            },
            /* onSuccess */
            function (_) { handle_login(formData.signup_email.value, formData.signup_password.value); },
            /* onError */
            function (code) {
                switch (code) {
                    case 406:
                        msg = "Password length must be between 6 and 50 characters."
                        break;
                    case 409:
                        msg = "User already exists."
                        break;
                    case 400:
                    default:
                        msg = "Application error, try again."
                }
                communicateToUser(msg, "welcome_view");
            })
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
    makeRequest("/sign_out", "POST", {}, function () { }, function () { }, true);
    transitionToWelcomeView();
}

function transitionToWelcomeView() {
    localStorage.removeItem("token");
    displayView(false);
}

function changePassword(formData) {
    let psw = formData.change_password_input.value;
    let repeatPsw = formData.repeat_change_password_input.value;
    let repeatPasswordInput = document.getElementById("repeat_change_password_input");
    let form = document.getElementById("change_password_form");

    if (validatePassword(psw, repeatPsw, repeatPasswordInput)) {
        makeRequest("/change_password", "POST",
            { "oldPassword": formData.current_password_input.value, "newPassword": psw },
            /* onSuccess */
            function (_) {
                form.reset();
                communicateToUser("Password changed.", "account_panel");
            },
            /* onError */
            function (code) {
                switch (code) {
                    case 401:
                        msg = "Wrong password or token expired, try again."
                        break;
                    case 406:
                        msg = "Password length must be between 6 and 50 characters."
                        break;
                    case 400:
                    default:
                        msg = "Application error, try again."
                }
                communicateToUser(msg, "account_panel");
            },
            true);
    }
}

function getUserInfo() {
    makeRequest("/get_user_data_by_token", "GET", {},
        /* onSuccess */
        function (data) {
            populateUserInfo(data, "home_panel");
        },
        /* onError */
        function (code) {
            switch (code) {
                case 401:
                    msg = "Token expired, try again."
                    break;
                case 400:
                default:
                    msg = "Application error, try again."
            }
            communicateToUser(msg, "home_panel");
        },
        true);
}

function populateUserInfo(data, panel) {
    document.getElementById(`${panel}_info_first_name`).innerText = data.firstname;
    document.getElementById(`${panel}_info_family_name`).innerText = data.familyname;
    document.getElementById(`${panel}_info_gender`).innerText = data.gender;
    document.getElementById(`${panel}_info_country`).innerText = data.country;
    document.getElementById(`${panel}_info_city`).innerText = data.city;
    document.getElementById(`${panel}_info_email`).innerText = data.email;
}

function postMessage(formData, postToFoundUser = false) {
    let panel = postToFoundUser ? "browse_panel" : "home_panel";
    let toEmail = getUserEmail(panel);
    navigator.geolocation.getCurrentPosition(function (position) {
        makeRequest("/post_message", "POST",
            {
                "message": formData.post_message_textarea.value,
                "email": toEmail,
                "latitude": position.coords.latitude,
                "longitude": position.coords.longitude,
            },
            /* onSuccess */
            function (_) {
                document.getElementById(panel + "_post_message_form").reset();
                communicateToUser("Message posted.", panel);
            },
            /* onError */
            function (code) {
                switch (code) {
                    case 401:
                        msg = "Token expired, try again."
                        break;
                    case 406:
                        msg = "Message was too long."
                        break;
                    case 409:
                        msg = "No such user."
                        break;
                    case 400:
                    default:
                        msg = "Application error, try again."
                }
                communicateToUser(msg, panel);
            },
            true);
    });
}

function loadHomePanelMessageWall() {
    makeRequest("/get_user_messages_by_token", "GET", {},
        /* onSuccess */
        function (data) { populateMessageWall("home_panel", data);; },
        /* onError */
        function (code) {
            switch (code) {
                case 401:
                    msg = "Token expired, try again."
                    break;
                case 400:
                default:
                    msg = "Application error, try again."
            }
            communicateToUser(msg, "home_panel");
        },
        true);
}

function populateMessageWall(panel, data) {
    console.log(data)
    let feed = document.getElementById(panel + "_message_feed");
    let messages = "";
    data.forEach((msg) => messages += `<dt>${msg.writer} in ${msg.geolocation}</dt><dd draggable="true" ondragstart="dragMessage(event)">${msg.content}</dd>`);
    feed.innerHTML = `<dl>${messages}</dl>`;
}

function searchUser(formData) {
    let email = formData.user_email.value;
    makeRequest(`/get_user_data_by_email/${email}`, "GET", {},
        /* onSuccess */
        function (data) {
            document.getElementById("search_user_form").reset();
            populateUserInfo(data, "browse_panel");
            loadBrowsePanelMessageWall(email);
            toggleFoundUserInfo(true);
        },
        /* onError */
        function (code) {
            switch (code) {
                case 401:
                    msg = "Token expired, try again."
                    break;
                case 406:
                    msg = "No such user."
                    break;
                case 400:
                default:
                    msg = "Application error, try again."
            }
            communicateToUser(msg, "browse_panel");
            toggleFoundUserInfo(false);
        },
        true);
}

function loadBrowsePanelMessageWall(email) {
    makeRequest(`/get_user_messages_by_email/${email}`, "GET", {},
        /* onSuccess */
        function (data) { populateMessageWall("browse_panel", data); },
        /* onError */
        function (code) {
            switch (code) {
                case 401:
                    msg = "Token expired, try again."
                    break;
                case 406:
                    msg = "No such user."
                    break;
                case 400:
                default:
                    msg = "Application error, try again."
            }
            communicateToUser(msg, "browse_panel");
        },
        true);
}

function toggleFoundUserInfo(show) {
    let info = document.getElementById("user_info_group");
    if (show) {
        info.classList.remove("hidden_animation");
    } else {
        info.classList.add("hidden_animation");
    }
}

function setupSession() {
    let ws = new WebSocket(`ws://${window.location.hostname}:${window.location.port}/new_session`);

    ws.onopen = function () {
        ws.send(getToken());
    }

    ws.onmessage = function (message) {
        if (message.data == "signout") {
            transitionToWelcomeView();
        } else {
            data = JSON.parse(message.data);
            updateLiveData(data);
        }
    };

    ws.onerror = function () {
        // Sign out to be safe if an error occurs.
        signOut();
    };
}

// Allow drop for HTML Drag and Drop API
function allowDrop(ev) {
    ev.preventDefault();
}

// HTML Drag and Drop API for dragging a user message from the .
function dragMessage(ev) {
    ev.dataTransfer.setData("text", ev.target.innerText);
}

// HTML Drag and Drop API for dropping a user message in a text field.
function dropMessage(ev) {
    let textfield = document.getElementById(ev.target.id);
    textfield.value += ev.dataTransfer.getData("text");
    ev.preventDefault();
}

/**
 * Updates the Twidder Statistics chart.
 * @param {list{int}} data List with three integers. 
 */
function updateLiveData(data) {
    chart.data.datasets[0].data = data;
    chart.update();
}
