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


document.getElementById("createProjectButton").onclick = function() {	
    document.getElementById("repoLinkFieldErrorMessage").innerHTML = "";
    document.getElementById("nameFieldErrorMessage").innerHTML = "";
	const url = document.getElementById("createProjectButton").getAttribute("href");
	const projectName = document.getElementById("newProjectName").value;
    const projectRepoLink = document.getElementById("newProjectRepoLink").value; 
    const filesFolder = document.getElementById("newProjectFilesFolder").value;
    const gitAccessToken = document.getElementById("newProjectGitAccessToken").value;
    const gitUser = document.getElementById("newProjectGitUsername").value;
    const smartMode = document.getElementById("newProjectSmartMode").checked;
    const commonAutoTestsFolder = document.getElementById("newProjectCommonAutoTestsFolder").value;
    const data = JSON.stringify({"name": projectName,
                                 "repo_url": projectRepoLink,
                                 "files_folder": filesFolder,
                                 "smart_mode": smartMode,
                                 "git_access_key": gitAccessToken,
                                 "git_username": gitUser,
                                 "common_autotests_folder": commonAutoTestsFolder});
    let xhr = new XMLHttpRequest(); 
    xhr.open("POST", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(data);

    xhr.onload = function() {
    	let jsonResponse = JSON.parse(xhr.responseText);
        if (xhr.status >= 400){
            let jsonResponse = JSON.parse(xhr.responseText);
            if ("name" in jsonResponse){
                document.getElementById("nameFieldErrorMessage").innerHTML = jsonResponse["name"][0]    
            } 
            else if ("repo_url" in jsonResponse){
                document.getElementById("repoLinkFieldErrorMessage").innerHTML = jsonResponse["repo_url"][0]    
            }
            else if ("files_folder" in jsonResponse){
                document.getElementById("filesFolderFieldErrorMessage").innerHTML = jsonResponse["files_folder"][0]
            }
            else if ("common_autotests_folder" in jsonResponse){
                document.getElementById("commonAutoTestsFolderFieldErrorMessage").innerHTML = jsonResponse["common_autotests_folder"][0]
            }
        }
        else {
            window.location = "/";    
        }
    }

}