import React, { Component } from "react";
import { useState } from "react";
import {useRef} from "react";
import CodeMirror from "@uiw/react-codemirror";
import { StreamLanguage } from '@codemirror/language';
import { gherkin } from '@codemirror/legacy-modes/mode/gherkin';
import { indentUnit } from "@codemirror/language";


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

export default function AddFileModal(activeVersionId) {
  activeVersionId = activeVersionId.activeVersionId;
  const [fileName, setFileName] = useState("");
  const [fileText, setFileText] = useState("");
  const [isFormAccepted, setIsFormAccepted] = useState(false);
  const [fileNameError, setFileNameError] = useState("");
  const [fileTextError, setFileTextError] = useState("");

  const { pathname } = window.location;

  const handleFileNameChange = (event) => {
    setFileName(event.target.value);
  };

    const handleFileTextChange = React.useCallback((value, viewUpdate) => {
    setFileText(value);
  }, []);


  function createFile() {
    setFileNameError("");
    setFileTextError("");
    let xhr = new XMLHttpRequest();
    const url = "/api/create_file/";
    xhr.open("POST", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");


    xhr.onload = function () {
      let FileData = JSON.parse(xhr.responseText);
      if (xhr.status == 201) {

        closeModal.current.click();
        window.location.reload(false);
        return
      }
      if ("file_text" in FileData) {
        setFileTextError(FileData["file_text"])
        return
      }
      if ("file_name" in FileData) {
        setFileNameError(FileData["file_name"])
        return
      }
    }.bind(this);

    let data = {};
    data["project_version"] = activeVersionId;
    data["file_text"] = fileText;
    data["file_name"] = fileName;

    xhr.send(JSON.stringify(data));
  }
  const closeModal = useRef(null);

    return (
      <div>
        <button type="button"
                className="btn btn-outline-primary add-new-file-button"
                data-bs-toggle="modal"
                data-bs-target="#createFile"
                >+ Add New File</button>
        <div
          className="modal fade"
          id="createFile"
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
                  Add File
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                  ref={closeModal}
                ></button>
              </div>
              <div className="modal-body">
                <div className="input-group mb-3">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="File name"
                    aria-describedby="addon-wrapping"
                    id="newFileName"
                    onChange={handleFileNameChange}
                    value={fileName}
                  />
                </div>
                <div className="error-container">
                  <p className="text-danger field-error-message">
                    {fileNameError}
                  </p>
                </div>

                <div className="mb-3">
                    <CodeMirror
                      placeholder="File text"
                      value={fileText}
                      onChange={handleFileTextChange}
                      extensions={[StreamLanguage.define(gherkin),  indentUnit.of("    ")]}
                    />
                </div>
                <div className="error-container">
                  <p className="text-danger field-error-message">
                    {fileTextError}
                  </p>
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-primary"
                  id="createProjectButton"
                  onClick={createFile}
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
