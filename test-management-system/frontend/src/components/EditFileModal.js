import React, { Component } from "react";
import { useState } from "react";
import {useRef} from "react";

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

export default function EditFileModal({
    activeVersionId,
    activeTestFileId,
    activeTestFileName
}) {

  const [fileName, setFileName] = useState("");
  const [fileText, setFileText] = useState("");
  const [isFormAccepted, setIsFormAccepted] = useState(true);
  const [textAccepted, setTextAccepted] = useState(false);
  const [fileNameError, setFileNameError] = useState("");
  const [fileTextError, setFileTextError] = useState("");
  const [fileNameChanged, setFileNameChanged] = useState(false);
  const [fileTextChanged, setFileTextChanged] = useState(false);

  const { pathname } = window.location;


  const handleFileNameChange = (event) => {
    setFileNameChanged(true);
    setFileName(event.target.value);
  };

  const handleFileText = (event) => {
    setFileTextChanged(true);
    setFileText(event.target.value);
  };

  function editFile() {
    setFileNameError("");
    setFileTextError("");
    let xhr = new XMLHttpRequest();
    const url = "/api/update_file/" + activeTestFileId + "/";
    xhr.open("PUT", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");


    xhr.onload = function () {
      if (xhr.status >= 500) {
        closeModal.current.click();
        return
      }
      let fileData = JSON.parse(xhr.responseText);
      if (xhr.status == 200) {
        closeModal.current.click();
        window.location.reload(false);
        return
      }
      if ("file_text" in fileData) {
        setFileTextError(fileData["file_text"])
        return
      }
      if ("file_name" in fileData) {
        setFileNameError(fileData["file_name"])
        return
      }
    }.bind(this);

    let data = {};

    if (fileNameChanged) {
        data["file_name"] = fileName;
    }
    if (fileTextChanged) {
        data["file_text"] = fileText;
    }
    xhr.send(JSON.stringify(data));
  }
  const closeModal = useRef(null);
  const modal = useRef(null);

  let openModal = () => {
    let xhr = new XMLHttpRequest();
    const url = "/api/get_file_text/" + activeTestFileId + "/";
    xhr.open("GET", url);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
      if (xhr.status == 200) {
        setTextAccepted(true);
        setFileText(xhr.responseText);
        setFileName(activeTestFileName);
        return
      }
      else {
        closeModal.current.click();
      }
    }.bind(this);
    xhr.send();

  }
  let textAreaElement = undefined;
  let fileNameElement = undefined;
  if (textAccepted) {
    textAreaElement = (
        <textarea
         className="form-control"
         id="edited-file-text"
         placeholder="File text"
         value={fileText}
         onChange={handleFileText}
         rows="20"
         >
         </textarea>)

   fileNameElement = (
       <input
        type="text"
        className="form-control"
        placeholder="File name"
        aria-describedby="addon-wrapping"
        id="editFileName"
        onChange={handleFileNameChange}
        value={fileName}
      />
   )
  } else {
    textAreaElement = (
        <textarea
         className="form-control"
         id="edited-file-text"
         rows="20"
         readOnly="True"
         disabled
         >
   </textarea>)

   fileNameElement = (
       <input
        type="text"
        className="form-control"
        aria-describedby="addon-wrapping"
        id="editFileName"
        onChange={handleFileNameChange}
        value={fileName}
        disabled
      />
   )
  }

    return (
      <div className="file-action">
        <button type="button"
                className="btn btn-primary btn-lg"
                data-bs-toggle="modal"
                data-bs-target="#editFile"
                onClick={openModal}>
                    Edit File
                </button>
        <div
          className="modal fade"
          id="editFile"
          data-bs-backdrop="static"
          data-bs-keyboard="false"
          tabIndex="-1"
          aria-labelledby="staticBackdropLabel"
          aria-hidden="true"
        >
          <div className="modal-dialog modal-lg modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title" id="staticBackdropLabel">
                  Edit File
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
                    {fileNameElement}
                </div>
                <div className="error-container">
                  <p className="text-danger field-error-message">
                    {fileNameError}
                  </p>
                </div>

                <div className="mb-3">
                   {textAreaElement}
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
                  id="editFileButton"
                  onClick={editFile}
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
}
