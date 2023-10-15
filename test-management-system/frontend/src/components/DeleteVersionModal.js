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

export default function DeleteVersionModal(version) {
  const { pathname } = window.location;
  const paths = pathname.split("/").filter((entry) => entry !== "");
  const [isButtonActive, setIsButtonActive] = useState(false);
  let versionLabel = version.version.version_label;
  let projectName = version.project;
  let versionId = version.version.id
  const requiredCodePhrase = projectName + "/" + versionLabel;

  let handleCodePhraseChange = (event) => {
    if (requiredCodePhrase == event.target.value) {
        setIsButtonActive(true);
    }
    else if (requiredCodePhrase != event.target.value) {
        setIsButtonActive(false);
    }
  }

  function deleteVersion() {
    let xhr = new XMLHttpRequest();
    const url = "/api/delete_version/" + versionId + "/";
    xhr.open("DELETE", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
        window.location.reload(false);
        return
    }.bind(this);
    xhr.send();
  }
  let deleteButton = undefined;

  if (isButtonActive) {
      deleteButton = (
                <button
                  type="button"
                  className="btn btn-danger"
                  id="createProjectButton"
                  onClick={deleteVersion}
                >
                  Delete Version
                </button>)
  } else {
      deleteButton = (
            <button
              type="button"
              className="btn btn-danger"
              id="createProjectButton"
              onClick={deleteVersion}
              disabled
            >
              Delete Version
            </button>)
  }

    return (
      <div>
        <button
          type="button"
          className="btn btn-outline-danger"
          data-bs-toggle="modal"
          data-bs-target="#deleteVersion"
        >
          Delete Version
        </button>
        <div
          className="modal fade"
          id="deleteVersion"
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
                    Delete Version
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body">
                <p className="text-danger">It will delete this version with all .feature files! </p>
                <div className="composite-text"> <p> To confirm action type </p> <b>{requiredCodePhrase}</b> </div>
                <div className="input-group mb-3">
                  <input
                    type="text"
                    className="form-control"
                    aria-describedby="addon-wrapping"
                    id="codePhrase"
                    onChange={handleCodePhraseChange}
                  />
                </div>
              </div>
              <div className="modal-footer">
                {deleteButton}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
}
