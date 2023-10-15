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


document.getElementById("RegisterButton").onclick=function(){
    let url = document.getElementById("RegisterButton").getAttribute("href");
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    url += '?token=' + token;

    const email = document.getElementById("emailField").value;
    const name = document.getElementById("nameField").value;
    const password = document.getElementById("passwordField").value;
    const passwordConfirm = document.getElementById("passwordConfirmField").value;
    
    if (!email){
        document.getElementById("emailField").style.borderColor = wrongValueBorderField;
        return null;
    };

    if (!name){
        document.getElementById("nameField").style.borderColor = wrongValueBorderField;
        return null;
    };

    if (!password){
        document.getElementById("passwordField").style.borderColor = wrongValueBorderField;
        return null;
    };

    if (!email){
        document.getElementById("passwordConfirmField").style.borderColor = wrongValueBorderField;
        return null;
    };

    if (password != passwordConfirm){
        document.getElementById("passwordConfirmField").style.borderColor = wrongValueBorderField;
        document.getElementById("passwordConfirmFieldErrorMessage").innerHTML = "Passwords Don't Match";
        return null;      
    };

    let xhr = new XMLHttpRequest(); 
    xhr.open("POST", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");
    data = JSON.stringify({
            "email": email,
            "full_name": name,
            "password": password
        });

    xhr.send(data);

    xhr.onload = function() {
        if (xhr.status >= 400){
            let jsonResponse = JSON.parse(xhr.responseText);
            for(let errorField in jsonResponse) {
                let ErrorMessageFieldId = errorField + "FieldErrorMessage";
                document.getElementById(ErrorMessageFieldId).innerHTML = jsonResponse[errorField][0];
                };
            }
        else{
            window.location = "/login";
        }

    };

};


const formFields = document.getElementsByClassName("form-field");
for (let field of formFields){
    field.addEventListener("click", function onClick(event){
        event.target.style.borderColor = BorderField;
        let errorMessageId = event.target.id + "ErrorMessage";
        document.getElementById(errorMessageId).innerHTML = "";
    });
}


