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


function PerformLogout(){
	fetch('./user_api/logout/', {
        method: 'post',
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
    })
	window.location = "/login";
}



document.getElementById("generate-link").onclick = function() {	
	const url = document.getElementById("generate-link").getAttribute("href");
	let xhr = new XMLHttpRequest(); 
    xhr.open("GET", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.send();

    xhr.onload = function() {
    	let jsonResponse = JSON.parse(xhr.responseText);
        if (xhr.status >= 400){
        	return null
        }
        const url = jsonResponse["url"];
        document.getElementById("register-link").value = url;
    }

}


document.getElementById("copy-registration-link").onclick = function() {
  let urlToCopy = document.getElementById("register-link");
  urlToCopy.select();
  urlToCopy.setSelectionRange(0, 99999); 

  navigator.clipboard.writeText(urlToCopy.value);
}