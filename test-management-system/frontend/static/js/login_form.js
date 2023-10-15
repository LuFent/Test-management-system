function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


const wrongValueBorderField = "red";
const BorderField = "#ced4da";


document.getElementById("LoginButton").onclick=function(){
    const url = document.getElementById("LoginButton").getAttribute("href");
    const email = document.getElementById("emailField").value;
    const password = document.getElementById("passwordField").value;
    let xhr = new XMLHttpRequest(); 
    xhr.open("POST", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");   
    
    data = JSON.stringify({
            "email": email,
            "password": password
        });

    xhr.send(data);

    xhr.onload = function() {
    if (xhr.status >= 400){
        let jsonResponse = JSON.parse(xhr.responseText);
        for(let errorField in jsonResponse) {
            let FieldId = errorField + "Field"
            document.getElementById(FieldId).style.borderColor = wrongValueBorderField;
            }
        }
    else {
        window.location = "/"
    };
    };
};


const formFields = document.getElementsByClassName("form-field");
for (let field of formFields){
    field.addEventListener("click", function onClick(event){
        event.target.style.borderColor = BorderField;
    });
}