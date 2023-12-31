import React, { Component } from "react";
import { useState } from "react";

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export default function PushFilesModal(versionId) {

  const [updatedFiles, setUpdatedFiles] = useState(undefined);
  const [isFormAccepted, setIsFormAccepted] = useState(false);

  const { pathname } = window.location;
  const paths = pathname.split("/").filter((entry) => entry !== "");

  function openModal() {
    let xhr = new XMLHttpRequest();
    const url = "/api/get_updated_files/" + versionId.versionId + "/";
    xhr.open("GET", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
      if (xhr.status == 200) {
        let data = JSON.parse(xhr.responseText);
        let updatedFilesNames = []
        for(let fileIndex=0; fileIndex < data.length; fileIndex++){
              let updatedFile = data[fileIndex];
              updatedFilesNames.push(updatedFile.file_name_with_ext)
           }
        setUpdatedFiles(updatedFilesNames);
        return
      }
    }.bind(this);
    xhr.send();
  }

  function pushFiles() {
    let xhr = new XMLHttpRequest();
    const url = "/api/push_files/";
    xhr.open("POST", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
      if (xhr.status == 200) {
        setIsFormAccepted(true);
      }

    }.bind(this);

    let data = {};
    data["version_id"] = versionId.versionId;
    xhr.send(JSON.stringify(data));
  }
  let updatedFilesList = [];

  if (updatedFiles){
    for(let fileIndex=0; fileIndex < updatedFiles.length; fileIndex++){
      let updatedFile = updatedFiles[fileIndex];
      updatedFilesList.push(
        <li key={fileIndex}>{ updatedFile }</li>
      )
    }
  }
  if (isFormAccepted) {
    return (
      <div>
        <button
          type="button"
          className="btn btn-outline-secondary"
          data-bs-toggle="modal"
          data-bs-target="#pushFiles"
          onClick={() => {
            openModal();
            setIsFormAccepted(false);
          }}
        >
          Push Files
        </button>
        <div
          className="modal fade"
          id="pushFiles"
          data-bs-backdrop="static"
          data-bs-keyboard="false"
          tabIndex="-1"
          aria-labelledby="staticBackdropLabel"
          aria-hidden="true"
        >
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title" id="staticBackdropLabel">
                  Push Files
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body">
                <h3>Accepted, files will be pushed </h3>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  } else {
    return (
      <div>
        <button
          type="button"
          className="btn btn-outline-secondary"
          data-bs-toggle="modal"
          data-bs-target="#pushFiles"
          onClick={() => {
            openModal();
            setIsFormAccepted(false);
          }}
        >
          Push Files
        </button>
        <div
          className="modal fade"
          id="pushFiles"
          data-bs-backdrop="static"
          data-bs-keyboard="false"
          tabIndex="-1"
          aria-labelledby="staticBackdropLabel"
          aria-hidden="true"
        >
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title" id="staticBackdropLabel">
                  Push Files
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body">
              <p>This will push manually created files to remote repository</p>
              <p>Files to be pushed:</p>
              <ul>
              {updatedFilesList}
              </ul>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-primary"
                  id="createProjectButton"
                  onClick={pushFiles}
                >
                  Push Files
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
