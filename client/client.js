function displayView(signedIn) {
    view_id = signedIn ? "profile_view" : "welcome_view";
    document.getElementById("viewport").innerHTML = document.getElementById(view_id).innerHTML;
};

window.onload = function () {
    displayView(false);
};