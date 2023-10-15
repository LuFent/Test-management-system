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

export default function AddVersionModal() {
  const [versionName, setVersionName] = useState("");
  const [commit, setCommit] = useState("");
  const [branch, setBranch] = useState("");
  const [versionLabelError, setVersionLabelError] = useState("");
  const [isFormAccepted, setIsFormAccepted] = useState(false);

  const { pathname } = window.location;
  const paths = pathname.split("/").filter((entry) => entry !== "");
  const projectId = paths[paths.length - 1];

  const handleversionNameChange = (event) => {
    setVersionName(event.target.value);
  };

  const handleCommitChange = (event) => {
    setCommit(event.target.value);
  };

  const handleBranchChange = (event) => {
    setBranch(event.target.value);
  };

  function createVersion() {
    let xhr = new XMLHttpRequest();
    const url = "/api/create_version/";
    xhr.open("POST", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
      setVersionLabelError("");

      if (xhr.status == 200) {
        setIsFormAccepted(true);
        return
      }

      let versionData;
      versionData = JSON.parse(xhr.responseText);

      if ("version_label" in versionData) {
        setVersionLabelError(versionData["version_label"][0]);
      } else if ("non_field_errors" in versionData) {
        setVersionLabelError(
          "Such version label already exists in this project."
        );
      }
    }.bind(this);

    let data = {};
    data["project"] = projectId;
    data["version_label"] = versionName;
    data["commit_hash"] = commit;
    data["branch"] = branch;

    xhr.send(JSON.stringify(data));
  }
  if (isFormAccepted) {
    return (
      <div>
        <button
          type="button"
          className="btn btn-outline-secondary"
          data-bs-toggle="modal"
          data-bs-target="#createVersion"
          onClick={() => {
            setIsFormAccepted(false);
          }}
        >
          Add Version
        </button>
        <div
          className="modal fade"
          id="createVersion"
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
                  Создать весрию
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body">
                <h3>Accepted, new version will apear soon </h3>
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
          data-bs-target="#createVersion"
        >
          Add Version
        </button>
        <div
          className="modal fade"
          id="createVersion"
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
                  Create Version
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                ></button>
              </div>
              <div className="modal-body">
                <div className="input-group mb-3">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Version label"
                    aria-describedby="addon-wrapping"
                    id="newVersionLabel"
                    onChange={handleversionNameChange}
                    value={versionName}
                  />
                </div>
                <div className="error-container">
                  <p className="text-danger field-error-message">
                    {versionLabelError}
                  </p>
                </div>

                <div className="input-group mb-3">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Branch (leave empty for 'main')"
                    aria-label="RepoLink"
                    aria-describedby="addon-wrapping"
                    id="newVesionBracnhName"
                    onChange={handleBranchChange}
                    value={branch}
                  />
                </div>
                <div className="error-container">
                  <p
                    className="text-danger field-error-message"
                    id="branchFieldErrorMessage"
                  ></p>
                </div>

                <div className="input-group mb-3">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Commit SHA (leave empty for last commit)"
                    aria-label="RepoLink"
                    aria-describedby="addon-wrapping"
                    id="newProjectRepoLink"
                    onChange={handleCommitChange}
                    value={commit}
                  />
                </div>
                <div className="error-container">
                  <p
                    className="text-danger field-error-message"
                    id="repoLinkFieldErrorMessage"
                  ></p>
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-primary"
                  id="createProjectButton"
                  onClick={createVersion}
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
