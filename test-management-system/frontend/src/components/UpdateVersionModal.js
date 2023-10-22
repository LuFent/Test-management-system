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

export default function UpdateVersionModal(versionId) {
  const defaultBranchName = "main";

  const [isFormAccepted, setIsFormAccepted] = useState(false);

  const { pathname } = window.location;
  const paths = pathname.split("/").filter((entry) => entry !== "");
  const projectId = paths[paths.length - 1];

  const handleCommitChange = (event) => {
    setCommit(event.target.value);
  };

  const handleBranchChange = (event) => {
    setBranch(event.target.value);
  };

  function updateVersion() {
    let xhr = new XMLHttpRequest();
    const url = "/api/pull_version/";
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
  if (isFormAccepted) {
    return (
      <div>
        <button
          type="button"
          className="btn btn-outline-secondary"
          data-bs-toggle="modal"
          data-bs-target="#updateVersion"
          onClick={() => {
            setIsFormAccepted(false);
          }}
        >
          Update Version
        </button>
        <div
          className="modal fade"
          id="updateVersion"
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
                  Update Version
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body">
                <h3>Accepted, new tests will appear soon </h3>
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
          data-bs-target="#updateVersion"
        >
          Update Version
        </button>
        <div
          className="modal fade"
          id="updateVersion"
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
                  Update Version
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body">
              <p>This will update tests according to the last project commit in remote repository</p>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-primary"
                  id="createProjectButton"
                  onClick={updateVersion}
                >
                  Update
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
